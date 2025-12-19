"""
МОДУЛЬ: Фильтры нецензурных слов и оскорблений
Проверяет сообщения на наличие запрещённых слов и оскорблений.
Полностью независимый модуль - не зависит от других модулей.
"""

import re
from typing import List, Set


class MessageFilter:
    """Класс для фильтрации сообщений."""
    
    def __init__(self):
        """Инициализация списка запрещённых слов и оскорблений."""
        # Базовый список нецензурных слов (можно расширять)
        # ВАЖНО: Добавьте здесь реальные нецензурные слова
        # Используем set() для создания множества, а не {} (которое создаёт словарь)
        self.bad_words: Set[str] = set()
        # Примеры нецензурных слов (раскомментируйте и добавьте свои):
        # self.bad_words.add("слово1")
        # self.bad_words.add("слово2")
        
        # Список оскорблений (недопустимые выражения)
        self.insults: Set[str] = {
            # Оскорбления по внешности
            "урод", "уродина", "уродство",
            "дебил", "дебилка", "дебильный",
            "идиот", "идиотка", "идиотский",
            "дурак", "дура", "дурацкий", "дурость",
            "тупой", "тупая", "тупость",
            "кретин", "кретинка",
            "моральный урод",
            
            # Оскорбления по интеллекту
            "тупица", "тупоголовый",
            "безмозглый", "безмозглая",
            "тупорылый",
            "недоразвитый",
            
            # Оскорбления по характеру
            "сволочь", "сволочи",
            "подонок", "подонки",
            "мразь", "мрази",
            "гад", "гадина",
            "тварь",
            "скотина",
            "животное",
            "отброс",
            "отморозок",
            
            # Грубые оскорбления
            "козел", "козлина",
            "осел", "ослица",
            "свинья",
            "собака",
            "крыса",
            "змея",
            
            # Матерные слова (проверяются также через регулярные выражения)
            "блядь", "бля",
            "хуй", "хуйня",
            "пизда", "пиздец",
            "ебанутый", "ебать",
            "говно",
            "заебись",
            "ублюдок",
            
            # Оскорбления в адрес семьи
            "мать твою",
            "твою мать",
            "твою мамашу",
            
            # Унизительные выражения
            "ничтожество",
            "ничего не стоишь",
            "никчемный",
            "бесполезный",
            "никому не нужен",
            
            # Угрозы и агрессия
            "убью", "убить",
            "задушу", "задушить",
            "изобью", "избить",
            "порву", "порвать",
            
            # Оскорбления по национальности/расе (недопустимо)
            "черножопый",
            "чурка",
            "хач",
            
            # Оскорбления по полу
            "шлюха",
            "проститутка",
            "сука",
            "сукин сын",
        }
        
        # Объединяем все запрещённые слова
        # Используем union для объединения множеств
        self.bad_words = self.bad_words.union(self.insults)
        
        # Регулярные выражения для более сложной фильтрации
        # Обнаружение слов с заменой букв для обхода фильтра
        self.patterns: List[re.Pattern] = [
            # Мат с заменой букв (б*ядь, х*й, бл@дь и т.д.)
            re.compile(r'б[л*@]', re.IGNORECASE),
            re.compile(r'б[л*@][я*@]д', re.IGNORECASE),
            re.compile(r'х[у*@]й', re.IGNORECASE),
            re.compile(r'п[и*@]зд', re.IGNORECASE),
            re.compile(r'е[б*@]а', re.IGNORECASE),
            re.compile(r'г[о*@]вн', re.IGNORECASE),
            re.compile(r'з[а@*]б[и*@]сь', re.IGNORECASE),
            re.compile(r'у[б*@]люд', re.IGNORECASE),
            
            # Оскорбления с заменой букв
            re.compile(r'д[е*@]б[и*@]л', re.IGNORECASE),
            re.compile(r'и[д*@]и[о*@]т', re.IGNORECASE),
            re.compile(r'к[р*@]ет[и*@]н', re.IGNORECASE),
            re.compile(r'т[у*@]п[о*@]й', re.IGNORECASE),
            
            # Обход через звёздочки и специальные символы
            re.compile(r'[бБ][*@]', re.IGNORECASE),
            re.compile(r'[хХ][*@]', re.IGNORECASE),
            re.compile(r'[пП][*@]', re.IGNORECASE),
            re.compile(r'[сС][у*@]к', re.IGNORECASE),
            
            # Попытки обхода через пробелы внутри слова
            re.compile(r'б\s*л\s*я\s*д', re.IGNORECASE),
            re.compile(r'х\s*у\s*й', re.IGNORECASE),
        ]
    
    def add_word(self, word: str):
        """
        Добавляет слово в список запрещённых.
        
        Args:
            word: Запрещённое слово
        """
        self.bad_words.add(word.lower())
    
    def add_pattern(self, pattern: str):
        """
        Добавляет регулярное выражение для фильтрации.
        
        Args:
            pattern: Регулярное выражение
        """
        self.patterns.append(re.compile(pattern, re.IGNORECASE))
    
    def contains_bad_words(self, text: str) -> bool:
        """
        Проверяет, содержит ли текст запрещённые слова.
        
        Args:
            text: Текст для проверки
            
        Returns:
            True если содержит запрещённые слова, False иначе
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Проверка по списку слов
        for word in self.bad_words:
            if word in text_lower:
                return True
        
        # Проверка по регулярным выражениям
        for pattern in self.patterns:
            if pattern.search(text):
                return True
        
        return False
    
    def find_bad_words(self, text: str) -> List[str]:
        """
        Находит все запрещённые слова в тексте.
        
        Args:
            text: Текст для проверки
            
        Returns:
            Список найденных запрещённых слов
        """
        found_words = []
        
        if not text:
            return found_words
        
        text_lower = text.lower()
        
        # Поиск по списку слов
        for word in self.bad_words:
            if word in text_lower:
                found_words.append(word)
        
        # Поиск по регулярным выражениям
        for pattern in self.patterns:
            matches = pattern.findall(text)
            found_words.extend(matches)
        
        return list(set(found_words))  # Убираем дубликаты


# Глобальный экземпляр фильтра
message_filter = MessageFilter()

