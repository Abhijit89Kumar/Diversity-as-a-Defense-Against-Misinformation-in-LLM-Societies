"""Analysis pipeline.

Reads from logged trajectory data only. Never re-hits an inference API to regenerate an
analysis: provider and sampling outputs are not reproducible, and the logged trajectory
dataset is the durable artefact (SOP-040 SS2).
"""
