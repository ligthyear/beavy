import warnings

warnings.warn("IncludingHyperlinkRelated is deprecated in favor for" +
              "IncludingRelationShip. Please use that one!",
              category=DeprecationWarning)

from .including_relationship import IncludingRelationShip

IncludingHyperlinkRelated = IncludingRelationShip
