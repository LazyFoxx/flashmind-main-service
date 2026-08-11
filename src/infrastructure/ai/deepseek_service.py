import json
from datetime import date
from typing import Optional
import json
from typing import List
from pydantic import BaseModel, Field, ValidationError

import httpx
import structlog

from src.application.interfaces.ai_service import (
    ModerationResult,
    AnalyzeStudyStatsResult,
    AnalyzeStatsInput,
    AIStudyAnalysisResult,
    AIInsight,
    AIProblemArea,
    AIRecommendation,
    AIGoals,
)
from src.application.interfaces import AbstractAIService
from src.core.settings import AISettings

logger = structlog.get_logger(__name__)


class DeepSeekAIService(AbstractAIService):
    def __init__(self, settings: AISettings):
        self.settings = settings
        self.api_key = settings.api_key.get_secret_value()
        self.model = settings.model
        self.base_url = settings.base_url.rstrip("/")
        self.api_url = f"{self.base_url}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _chat_completion(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.7,
        is_json: bool = True,
    ) -> str:
        messages_with_system = [
            {"role": "system", "content": system_prompt}
        ] + messages
        client_base_url = f"{self.api_url}/"

        async with httpx.AsyncClient(
            base_url=client_base_url,
            headers=self.headers,
            timeout=300.0,
        ) as client:
            payload = {
                "model": self.model,
                "messages": messages_with_system,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            # Включаем JSON-формат только если флаг True
            if is_json:
                payload["response_format"] = {"type": "json_object"}

            response = await client.post("", json=payload)
            response.raise_for_status()

            # --- ДЕБАГ-ПРИНТ ---
            print("--- RAW DEEPSEEK RESPONSE ---")
            print(response.text)
            print("--------------------------------")
            # ---------------------

            data = response.json()

            # --- ЛОГИРОВАНИЕ И РАСЧЕТ СТОИМОСТИ ---
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

            # Разбивка кэша (специфика DeepSeek)
            cache_hit = usage.get("prompt_cache_hit_tokens", 0)
            cache_miss = usage.get("prompt_cache_miss_tokens", 0)

            # Расчет стоимости для deepseek-v4-flash (цены за 1 токен)
            cost_hit = cache_hit * (0.0028 / 1_000_000)
            cost_miss = cache_miss * (0.14 / 1_000_000)
            cost_output = completion_tokens * (0.28 / 1_000_000)
            total_cost = cost_hit + cost_miss + cost_output

            # Выводим в логгер структурированную информацию
            logger.info(
                "DeepSeek request processed",
                total_tokens=usage.get("total_tokens"),
                cache_hit_tokens=cache_hit,
                cache_miss_tokens=cache_miss,
                output_tokens=completion_tokens,
                estimated_cost_usd=f"${total_cost:.8f}",
            )

            return data["choices"][0]["message"]["content"].strip()

    async def moderate_public_deck(
        self,
        deck_name: str,
        deck_description: str,
        user_name: str,
        user_bio: Optional[str],
        sample_cards: list[tuple[str, str]],
    ) -> ModerationResult:
        """Модерировать публичную колоду через DeepSeek API."""

        # Системный промпт для moderate_public_deck
        SYSTEM_PROMPT = """\
You are an automated content moderation backend system for a spaced repetition flashcards learning application.

### Tasks
Analyze the user-submitted flashcard deck data against the strict moderation criteria below.

### Moderation Criteria
1. **Violence**: Absolutely prohibited.
2. **Politics**: Absolutely prohibited.
3. **Religion**: Allowed only for purely educational or historical contexts. Prohibit dogmatic, preachy, or extremist content.
4. **Profanity**: Prohibit obscene language, slurs, and explicit profanity.
5. **Inappropriate content**: Prohibit NSFW, adult content, or hate speech.
6. **Coherence**: Ensure the deck name, description, and individual flashcards are logically and topically related.
7. **Quality**: Reject nonsense, spam, placeholder text (e.g., "test", "bla bla", "lorem ipsum"), or decks with zero educational value.

### Language Requirement
- The analyzed content might be in Russian or another language.
- If the content is in Russian and is REJECTED, write the "reason" field in Russian so the user can understand it.

### Output JSON Format Specification
You must respond with a raw JSON object matching this exact schema:
{
  "approved": boolean,
  "reason": string,
  "severity": "low" | "medium" | "high"
}

### Rules for JSON Fields:
- If "approved" is true: the "reason" field MUST be an empty string "".
- If "approved" is false: provide a clear, concise explanation of the violation in the "reason" field, and set the appropriate "severity".
- Do not output any markdown formatting, wrappers like ```json, or conversational filler. Return only the raw JSON string.
"""

        # Формируем cards_text
        cards_text = "\n".join(
            f"{i+1}. Front: {front}\n   Back: {back}"
            for i, (front, back) in enumerate(sample_cards)
        )

        user_prompt = f"""\
Review the following content for a public flashcards deck.

## Deck Information
- **Name**: {deck_name}
- **Description**: {deck_description}
- **User**: {user_name}
- **Bio**: {user_bio or 'N/A'}

## Sample Cards (up to 10)
{cards_text}

## Review Tasks
1. Check for violence, politics, religion, profanity, inappropriate content
2. Check coherence: does the name match the cards?
3. Check quality: is it meaningful educational content or nonsense?

Return JSON with approved status.
"""

        try:
            content = await self._chat_completion(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=SYSTEM_PROMPT,
                max_tokens=500,
                temperature=0.1,
            )
            result = json.loads(content)

            return ModerationResult(
                approved=result.get("approved", False),
                reason=result.get("reason", "Неизвестная причина"),
                severity=result.get("severity", "medium"),
            )

        except (KeyError, IndexError) as e:
            logger.error("DeepSeek API parse error", detail=str(e))
            return ModerationResult(
                approved=False,
                reason="Ошибка обработки AI",
                severity="high",
            )
        except json.JSONDecodeError as e:
            logger.error("DeepSeek JSON parse error", detail=str(e))
            return ModerationResult(
                approved=False,
                reason="Ошибка обработки AI",
                severity="high",
            )
        except httpx.HTTPStatusError as e:
            logger.error("DeepSeek API error", status=e.response.status_code)
            return ModerationResult(
                approved=False,
                reason="Сервис AI недоступен",
                severity="medium",
            )
    async def analyze_study_stats(
        self,
        input_data: AnalyzeStatsInput,
    ) -> AnalyzeStudyStatsResult:
        """Анализировать статистику обучения пользователя через DeepSeek API.

        Логика метода:
              1. Формируем контекст колоды (если есть input_data.deck)
              2. Формируем контекст сложных карточек (если есть input_data.hardest_cards)
              3. Формируем контекст сравнения (если есть previous_stats_json, previous_answer, previous_date)
              4. Формируем системный промпт с JSON-структурой ответа
              5. Формируем user_prompt с текущей статистикой
              6. Вызываем DeepSeek API, валидируем ответ и возвращаем DTO по параметрам
        """

           # ─── КОНТЕКСТ СРАВНЕНИЯ ────────────────────────────────────────
        comparison_context = ""
        has_comparison = (
             input_data.previous_stats_json is not None
             and input_data.previous_answer is not None
             and input_data.previous_date is not None
           )

        if has_comparison:
             previous_date_str = input_data.previous_date.isoformat()
             comparison_context = f"""

                   ### 📊 Сравнение с предыдущим анализом ({previous_date_str} - дата создания анализа)

                 У вас есть данные за предыдущую неделю (возможно позже) ({previous_date_str}) для анализа трендов:

                   **Предыдущая статистика:**
                   {input_data.previous_stats_json}

                   **Предыдущий анализ:**
                   {input_data.previous_answer}

                 В вашем ответе обязательно включите:
                       1. 📈 Что стало ЛУЧШЕ за неделю (сравните метрики)
                       2. 📉 Что стало ХУЖЕ за неделю
                       3. 🎯 Какие новые цели стоит поставить
                       4. 💡 Конкретные рекомендации на основе трендов
                   """

           # ─── СИСТЕМНЫЙ ПРОМПТ ──────────────────────────────────────────
        SYSTEM_PROMPT = f"""Ты — высококлассный ( но очень дружелюбный ) специалист по анализу образовательных данных и когнитивный психолог в приложении для интервального повторения.
             Твоя задача: проанализировать учебные метрики пользователя, а затем вернуть структурированные инсайты, глобальную диагностику. Будь дружелюбным и оптимистичным.

             Имя пользователя: {input_data.user_name}

               ### Важный контекст:
               - Алгоритм FSRS рассчитывает интервалы автоматически на стороне приложения.

               ### Руководство по оценке метрик (Что обязательно нужно отразить):
               1. **Инсайты (insights)** Можешь указать тут хорошие метрики! Сделать прогнозы по будущему времени занятий и как скоро освоит материал ( если это разбор для одной колоды а не общий ):
               2. **Проблемные зоны (problem_areas)**: Обязательно отследи резкие падения успешности,регулярности. Найди свои закономерности, рост бэклога (просроченных карточек), признаки когнитивной усталости или плохие привычки (например, спам кнопкой "легко").
               3. **Рекомендации (recommendations)**: Обязательно дай конкретные советы по корректировке учебной нагрузки на следующие 7 дней
               4. **Цели** (goals): Ставь пользователю 3 цели на неделю на основе его показателей и/или сделай разбор предыдущих целей если они есть и выполнены ли они
               
               ### Формат вывода — ТОЛЬКО JSON

             Ты ДОЛЖЕН вернуть сырой JSON-объект строго со следующей структурой (все значения полей должны быть на русском языке):

               {{
               "insights": [
                   {{
                   "title": "Сфера фокуса (например: Удержание, Регулярность)",
                   "text": "Ключевой паттерн или достижение на основе Руководства выше. Около 20 слов на русском."
                   }}
               ],
               "problem_areas": [
                   {{
                   "title": "Выявленный риск (например: Рост долга, Усталость)",
                   "text": "Слабое место или ухудшающаяся метрика на основе Руководства выше. Около 20 слов на русском."
                   }}
               ],
               "recommendations": [
                   {{
                   "title": "Стратегия действий",
                   "text": "Конкретный глобальный совет на следующую неделю на основе Руководства выше. Около 30 слов на русском."
                   }}
               ],
               
               "goals": [
                    {{
                    "title": "Цели на неделю!",
                    "text": "Конкретные достижимые цели за неделю например снижение сложных карточек или других целей которые облегчат учебу и сделают более эффективной"
                    }}
                ],
               }}

               ### Строгие правила:
               1. Количество элементов в массивах: insights (1-5 пунктов), problem_areas (1-5 пунктов), recommendations (1-5 пунктов).
               3. Язык: Все текстовые значения пиши строго на русском языке.
               4. Чистый JSON: Верни ТОЛЬКО сырой JSON. НЕ оборачивай ответ в маркдаун-блоки типа ```json ... ```. Никакого вводного или финального текста вне JSON. Ответ должен начинаться прямо с {{ и заканчиваться }}.
               """

           # ─── USER PROMPT ───────────────────────────────────────────────
        user_prompt = f"""\
             Analyze the following study statistics for {input_data.user_name}.

               {comparison_context if has_comparison else "This is the first analysis — provide a baseline assessment."}

             Statistics data:
               {input_data.stats_json}
               """

           # ─── ВЫЗОВ API ─────────────────────────────────────────────────
        try:
            content = await self._chat_completion(
                 messages=[{"role": "user", "content": user_prompt}],
                 system_prompt=SYSTEM_PROMPT,
                 max_tokens=10000,
                 temperature=0.6,
                 is_json=True,
               )
             # Pydantic-модели для валидации ответа DeepSeek
            class InsightItem(BaseModel):
                title: str
                text: str

            class ProblemAreaItem(BaseModel):
                title: str
                text: str

            class RecommendationItem(BaseModel):
                title: str
                text: str
            
            class GoalsItem(BaseModel):
                title: str
                text: str

            class SpacedRepetitionAnalysis(BaseModel):
                insights: List[InsightItem]
                problem_areas: List[ProblemAreaItem]
                recommendations: List[RecommendationItem]
                goals: List[GoalsItem]


               # Валидируем через Pydantic — проверяет наличие всех полей и типов
            validated = SpacedRepetitionAnalysis.model_validate_json(content)

               # Формируем DTO по параметрам — каждый элемент преобразуется в свой dataclass
            result = AIStudyAnalysisResult(
                 insights=[
                     AIInsight(title=item.title, text=item.text)
                     for item in validated.insights
                  ],
                 problem_areas=[
                     AIProblemArea(title=item.title, text=item.text)
                     for item in validated.problem_areas
                  ],
                 recommendations=[
                     AIRecommendation(title=item.title, text=item.text)
                     for item in validated.recommendations
                  ],
                 goals=[
                     AIGoals(title=item.title, text=item.text)
                     for item in validated.goals
                 ]
              )

               # Логирование успешного результата
            logger.info(
                "AI stats analysis completed successfully",
                insights_count=len(result.insights),
                problem_areas_count=len(result.problem_areas),
                recommendations_count=len(result.recommendations),
              )

            return AnalyzeStudyStatsResult(status=True, result=result)

        except ValidationError as e:
             logger.error("DeepSeek validation error", detail=str(e))
             return AnalyzeStudyStatsResult(status=False, result=None)

        except httpx.HTTPStatusError as e:
            logger.error("DeepSeek HTTP error", status_code=e.response.status_code)
            return AnalyzeStudyStatsResult(status=False, result=None)

        except json.JSONDecodeError as e:
            logger.error("DeepSeek JSON parse error", detail=str(e))
            return AnalyzeStudyStatsResult(status=False, result=None)

        except Exception as e:
            logger.error("Unexpected error during AI analysis", detail=str(e))
            return AnalyzeStudyStatsResult(status=False, result=None)