import gin
from ssp.utils.ai_key_words import AIKeyWords


@gin.configurable
def get_positive_keywords():
    return AIKeyWords.POSITIVE.split("|")


@gin.configurable
def get_false_positive_keywords():
    return AIKeyWords.FALSE_POSITIVE.split("|")



