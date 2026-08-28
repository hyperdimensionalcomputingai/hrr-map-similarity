"""Public API for record-to-term adaptation and shared encoding."""

from .encoder import encode_all, encode_record, encode_terms
from .terms import Term, record_terms

__all__ = ["Term", "encode_all", "encode_record", "encode_terms", "record_terms"]
