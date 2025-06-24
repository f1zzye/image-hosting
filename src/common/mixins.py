from typing import Dict


class TitleMixin:
    title = None

    def get_context_data(self, **kwargs) -> Dict[str, object]:
        context = super(TitleMixin, self).get_context_data(**kwargs)
        context["title"] = self.title
        return context
