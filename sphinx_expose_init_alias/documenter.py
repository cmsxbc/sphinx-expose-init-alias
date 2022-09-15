from typing import Tuple, Any, Optional

import docutils.statemachine as doc_sm
import sphinx.ext.autodoc as autodoc
import sphinx.locale as sphinx_i18n


class AliasMember:
    def __init__(self, member):
        self._member = member

    @property
    def member(self):
        return self._member


def wrap_member(obj_member: autodoc.ObjectMember):
    return autodoc.ObjectMember(obj_member[0], AliasMember(obj_member[1]), *obj_member[2:])


class AliasModuleDocumenter(autodoc.ModuleDocumenter):
    objtype = 'aliasmodule'
    directivetype = autodoc.ModuleDocumenter.objtype
    priority = 10 + autodoc.ModuleDocumenter.priority
    option_spec = dict(autodoc.ModuleDocumenter.option_spec)

    def get_object_members(self, want_all: bool) -> Tuple[bool, autodoc.ObjectMembers]:
        _, members = super().get_object_members(want_all)
        prefix = f"{self.object.__name__}."
        ret = []
        for member in members:
            if not hasattr(member[1], "__module__"):
                continue
            if not member[1].__module__.startswith(prefix):
                continue
            ret.append(wrap_member(member))
        return False, ret


class AliasDocumenter(autodoc.ModuleLevelDocumenter):
    objtype = 'alias'
    directivetype = autodoc.DataDocumenter
    priority = 100000000

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
        return isinstance(member, AliasMember)

    def get_object_members(self, want_all: bool) -> Tuple[bool, autodoc.ObjectMembers]:
        return False, []

    def add_content(self, more_content: Optional[doc_sm.StringList]) -> None:
        if self.config.autodoc_typehints_format == "short":
            alias = autodoc.restify(self.object, "smart")
        else:
            alias = autodoc.restify(self.object)
        more_content = doc_sm.StringList([sphinx_i18n._('alias of %s') % alias], source='')
        for line, src in zip(more_content.data, more_content.items):
            self.add_line(line, src[0], src[1])
