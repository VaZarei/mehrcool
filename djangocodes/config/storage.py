from whitenoise.storage import CompressedManifestStaticFilesStorage


class HashedModuleStaticFilesStorage(CompressedManifestStaticFilesStorage):
    support_js_module_import_aggregation = True
