from django import template

from .. import i18n

register = template.Library()


@register.simple_tag(takes_context=True)
def t(context, key: str) -> str:
    """Translate a UI string into the active dialect."""

    lang = context.get("dw_lang", i18n.DEFAULT_LANG)
    return i18n.get_string(key, lang)


@register.filter
def function_blurb(function, lang: str = i18n.DEFAULT_LANG) -> str:
    meta = function.meta
    return meta["blurb"].get(lang) or meta["blurb"][i18n.DEFAULT_LANG]


@register.filter
def legacy_to_code(value: str) -> str:
    return i18n.normalise(value)


@register.simple_tag
def bihari_function(code: str) -> dict:
    from .. import bihari

    return bihari.get_function(code)
