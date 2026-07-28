from typing import List, Optional

from pydantic import BaseModel, Field


class OneTimeMetricsResponse(BaseModel):
    """Разовые метрики: общее время изучения."""
    total_study_seconds: int = Field(
        ...,
        description="Общее время изучения в секундах",
        examples=[45630],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_study_seconds": 45630,
                 }
             ]
        }
    }


class ForecastPoint(BaseModel):
    """Точка графика прогноза."""
    date: str = Field(
        ...,
        description="Дата в формате YYYY-MM-DD",
        examples=["2023-10-25"],
    )
    count: int = Field(
        ...,
        description="Количество карточек на повтор",
        examples=[10],
    )


class ForecastResponse(BaseModel):
    """Прогноз: количество карточек на повтор на ближайшие дни."""
    points: List[ForecastPoint] = Field(
        ...,
        description="Данные для столбчатой диаграммы (30 или 180 дней)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "points": [
                        {"date": "2023-10-25", "count": 4},
                        {"date": "2023-10-26", "count": 10},
                     ]
                 }
             ]
        }
    }


class ReviewCountPoint(BaseModel):
    """Точка графика повторений."""
    date: str = Field(
        ...,
        description="Дата в формате YYYY-MM-DD",
        examples=["2023-10-25"],
    )
    forgotten: int = Field(
        ...,
        description="Количество ответов 'Забыл' (красный)",
        examples=[2],
    )
    hard: int = Field(
        ...,
        description="Количество ответов 'Сложно' (желтый)",
        examples=[1],
    )
    good: int = Field(
        ...,
        description="Количество ответов 'Хорошо' (желтый/зеленый граница)",
        examples=[2],
    )
    easy: int = Field(
        ...,
        description="Количество ответов 'Легко' (зеленый)",
        examples=[5],
    )

    @property
    def total(self) -> int:
        return self.forgotten + self.hard + self.good + self.easy


class ReviewCountResponse(BaseModel):
    """Повторения: общее число ответов карточек по дням."""
    points: List[ReviewCountPoint] = Field(
        ...,
        description="Данные для столбчатой диаграммы (последние 30 дней)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "points": [
                        {
                             "date": "2023-10-25",
                             "forgotten": 2,
                             "hard": 1,
                             "good": 2,
                             "easy": 5,
                         }
                     ]
                 }
             ]
        }
    }


class ReviewTimePoint(BaseModel):
    """Точка графика времени."""
    date: str = Field(
        ...,
        description="Дата в формате YYYY-MM-DD",
        examples=["2023-10-25"],
    )
    seconds: int = Field(
         ...,
        description="Суммарное время в секундах",
        examples=[900],
     )


class ReviewTimeResponse(BaseModel):
    """Время: суммарное время учебы ежедневно."""
    points: List[ReviewTimePoint] = Field(
         ...,
        description="Данные для графика времени по дням",
     )

    model_config = {
          "json_schema_extra": {
              "examples": [
                  {
                       "points": [
                           {"date": "2023-10-25", "seconds": 900},
                           {"date": "2023-10-26", "seconds": 1200},
                       ]
                   }
               ]
          }
      }


class HourlyBreakdownPoint(BaseModel):
    """Точка графика продуктивности по часам."""
    hour_range: str = Field(
         ...,
        description="Диапазон часов (например, '00:00-04:00')",
        examples=["00:00-04:00"],
     )
    percentage: float = Field(
          ...,
        ge=0,
        le=100,
        description="Процент правильно отвеченных (Хорошо и Легко) от всех ответов в этом диапазоне",
        examples=[85.5],
      )


class HourlyBreakdownResponse(BaseModel):
    """Объем карточек: продуктивность по часам суток."""
    points: List[HourlyBreakdownPoint] = Field(
          ...,
        description="Распределение по 6 столбам (каждые 4 часа) в процентах успеха",
      )

    model_config = {
          "json_schema_extra": {
              "examples": [
                  {
                       "points": [
                           {"hour_range": "00:00-04:00", "percentage": 70.0},
                           {"hour_range": "04:00-08:00", "percentage": 85.0},
                           {"hour_range": "08:00-12:00", "percentage": 92.0},
                           {"hour_range": "12:00-16:00", "percentage": 88.0},
                           {"hour_range": "16:00-20:00", "percentage": 75.0},
                           {"hour_range": "20:00-24:00", "percentage": 60.0},
                       ]
                   }
               ]
          }
      }


class DifficultyDistributionPoint(BaseModel):
    """Точка распределения по сложности."""
    range_label: str = Field(
        ...,
        description="Диапазон сложности (например, '1-2', '2-3' ... '9-10')",
        examples=["1-2"],
    )
    count: int = Field(
        ...,
        description="Количество карточек в диапазоне сложности",
        examples=[10],
     )


class DifficultyDistributionResponse(BaseModel):
    """Распределение изучаемых карточек по сложности."""
    points: List[DifficultyDistributionPoint] = Field(
        ...,
        description="Столбцы с диапазонами сложности от 1 до 9+",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "points": [
                        {"range_label": "1-2", "count": 2},
                        {"range_label": "2-3", "count": 5},
                        {"range_label": "3-4", "count": 10},
                        {"range_label": "4-5", "count": 15},
                        {"range_label": "5-6", "count": 20},
                        {"range_label": "6-7", "count": 18},
                        {"range_label": "7-8", "count": 12},
                        {"range_label": "8-9", "count": 8},
                        {"range_label": "9-10", "count": 3},
                    ]
                }
            ]
        }
    }


class StabilityDistributionPoint(BaseModel):
    """Точка распределения по стабильности."""
    range_label: str = Field(
         ...,
        description="Диапазон дней в который попадает карточка которую пользователь вспомнит с вероятностью 90% (например, '1-25 дней')",
        examples=["1-25 дней"],
     )
    count: int = Field(
         ...,
        description="Количество карточек в диапазоне",
        examples=[50],
     )


class StabilityDistributionResponse(BaseModel):
    """Распределение изучаемых карточек по стабильности."""
    points: List[StabilityDistributionPoint] = Field(
         ...,
        description="4 столбца: 1-25, 25-50, 50-100, >100 дней. Через сколько дней вероятность вспомнить карточку = 0.9",
     )

    model_config = {
          "json_schema_extra": {
              "examples": [
                  {
                       "points": [
                           {"range_label": "1-25 дней", "count": 10},
                           {"range_label": "25-50 дней", "count": 20},
                           {"range_label": "50-100 дней", "count": 30},
                           {"range_label": ">100 дней", "count": 40},
                       ]
                   }
               ]
          }
      }


class CardTypePoint(BaseModel):
    """Точка круговой диаграммы типов карт."""
    card_type: str = Field(
         ...,
        description="Тип карты: 'новые', 'изучаемые', 'изученные', 'отложенные'",
        examples=["новые"],
     )
    count: int = Field(
         ...,
        description="Количество карт данного типа",
        examples=[100],
     )


class CardTypeResponse(BaseModel):
    """Типы карт: количество карт по типам."""
    points: List[CardTypePoint] = Field(
         ...,
        description="Новые, Изучаемые, Изученные, Отложенные",
     )

    model_config = {
         "json_schema_extra": {
             "examples": [
                 {
                      "points": [
                          {"card_type": "новые", "count": 10},
                          {"card_type": "изучаемые", "count": 45},
                          {"card_type": "изученные", "count": 50},
                          {"card_type": "отложенные", "count": 5},
                      ]
                  }
              ]
         }
     }


class StudyStatsResponse(BaseModel):
    """
    Общий ответ со всеми статистическими данными.
    Содержит разовые метрики и все графики.
    """
    one_time_metrics: OneTimeMetricsResponse = Field(
          ...,
        description="Разовые метрики (общее время изучения)",
      )
    forecast: ForecastResponse = Field(
          ...,
        description="Прогноз повторений на ближайшие дни",
      )
    review_count: ReviewCountResponse = Field(
          ...,
        description="График повторений (ответы по дням)",
      )
    review_time: ReviewTimeResponse = Field(
          ...,
        description="График времени обучения (секунды по дням)",
      )
    hourly_breakdown: HourlyBreakdownResponse = Field(
           ...,
        description="Продуктивность по часам суток (процент успеха)",
       )
    difficulty_distribution: DifficultyDistributionResponse = Field(
          ...,
        description="Распределение карточек по сложности",
      )
    stability_distribution: StabilityDistributionResponse = Field(
          ...,
        description="Распределение карточек по стабильности",
      )
    card_types: CardTypeResponse = Field(
          ...,
        description="Типы карт (количество по типам)",
      )

    model_config = {
         "json_schema_extra": {
             "examples": [
                 {
                     "one_time_metrics": {
                         "total_study_seconds": 45630,
                     },
                     "forecast": {
                         "points": [
                             {"date": "2023-10-25", "count": 4},
                             {"date": "2023-10-26", "count": 10},
                         ]
                     },
                     "review_count": {
                         "points": [
                             {
                                 "date": "2023-10-25",
                                 "forgotten": 2,
                                 "hard": 1,
                                 "good": 2,
                                 "easy": 5,
                             }
                         ]
                     },
                     "review_time": {
                         "points": [
                             {"date": "2023-10-25", "seconds": 900},
                             {"date": "2023-10-26", "seconds": 1200},
                         ]
                     },
                     "hourly_breakdown": {
                         "points": [
                             {"hour_range": "00:00-04:00", "percentage": 70.0},
                             {"hour_range": "04:00-08:00", "percentage": 85.0},
                             {"hour_range": "08:00-12:00", "percentage": 92.0},
                             {"hour_range": "12:00-16:00", "percentage": 88.0},
                             {"hour_range": "16:00-20:00", "percentage": 75.0},
                             {"hour_range": "20:00-24:00", "percentage": 60.0},
                         ]
                     },
                     "difficulty_distribution": {
                         "points": [
                             {"range_label": "1-2", "count": 2},
                             {"range_label": "2-3", "count": 5},
                             {"range_label": "3-4", "count": 10},
                             {"range_label": "4-5", "count": 15},
                             {"range_label": "5-6", "count": 20},
                             {"range_label": "6-7", "count": 18},
                             {"range_label": "7-8", "count": 12},
                             {"range_label": "8-9", "count": 8},
                             {"range_label": "9-10", "count": 3},
                         ]
                     },
                     "stability_distribution": {
                         "points": [
                             {"range_label": "1-25 дней", "count": 10},
                             {"range_label": "25-50 дней", "count": 20},
                             {"range_label": "50-100 дней", "count": 30},
                             {"range_label": ">100 дней", "count": 40},
                         ]
                     },
                     "card_types": {
                         "points": [
                             {"card_type": "новые", "count": 10},
                             {"card_type": "изучаемые", "count": 45},
                             {"card_type": "изученные", "count": 50},
                             {"card_type": "отложенные", "count": 5},
                         ]
                     },
                 }
             ]
         }
     }
