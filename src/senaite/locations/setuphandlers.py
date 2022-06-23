from bika.lims import api
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import INonInstallable
from senaite.locations import logger
from senaite.locations import PRODUCT_NAME
from senaite.locations import PROFILE_ID
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.setuphandlers import setup_other_catalogs
from zope.component import getUtility
from zope.interface import implementer

# Tuples of (catalog, index_name, index_attribute, index_type)
INDEXES = [
    (SAMPLE_CATALOG, "location", "", "FieldIndex"),
]

# Tuples of (catalog, column_name)
COLUMNS = [
    (SAMPLE_CATALOG, "isMedicalRecordTemporary"),
]

NAVTYPES = [
    "Location",
]

# An array of dicts. Each dict represents an ID formatting configuration
ID_FORMATTING = [
    {
        "portal_type": "Location",
        "form": "Loc{seq:06d}",
        "prefix": "location",
        "sequence_type": "generated",
        "counter_type": "",
        "split_length": 1,
    }
]


def setup_handler(context):
    """Generic setup handler"""
    import pdb; pdb.set_trace()  # fmt: skip
    if context.readDataFile("{}.txt".format(PRODUCT_NAME)) is None:
        return

    logger.info("{} setup handler [BEGIN]".format(PRODUCT_NAME.upper()))
    portal = context.getSite()

    update_client_allowed_types(portal)

    # Configure visible navigation items
    setup_navigation_types(portal)

    # Setup catalogs
    setup_catalogs(portal)

    # Apply ID format to content types
    setup_id_formatting(portal)

    logger.info("{} setup handler [DONE]".format(PRODUCT_NAME.upper()))


def pre_install(portal_setup):
    """Runs before the first import step of the *default* profile
    This handler is registered as a *pre_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} pre-install handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_ID)  # noqa
    portal = context.getSite()  # noqa

    logger.info("{} pre-install handler [DONE]".format(PRODUCT_NAME.upper()))


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} install handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_ID)  # noqa
    portal = context.getSite()  # noqa

    logger.info("{} install handler [DONE]".format(PRODUCT_NAME.upper()))


def post_uninstall(portal_setup):
    """Runs after the last import step of the *uninstall* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} uninstall handler [BEGIN]".format(PRODUCT_NAME.upper()))

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = "profile-{}:uninstall".format(PRODUCT_NAME)
    context = portal_setup._getImportContext(profile_id)  # noqa
    portal = context.getSite()  # noqa
    remove_client_allowed_types(portal)
    logger.info("{} uninstall handler [DONE]".format(PRODUCT_NAME.upper()))


def setup_navigation_types(portal):
    """Add additional types for navigation"""
    registry = getUtility(IRegistry)
    key = "plone.displayed_types"
    display_types = registry.get(key, ())

    new_display_types = set(display_types)
    new_display_types.update(NAVTYPES)
    registry[key] = tuple(new_display_types)


def setup_id_formatting(portal, format_definition=None):
    """Setup default ID formatting"""
    if not format_definition:
        logger.info("Setting up ID formatting ...")
        for formatting in ID_FORMATTING:
            setup_id_formatting(portal, format_definition=formatting)
        logger.info("Setting up ID formatting [DONE]")
        return

    bs = portal.bika_setup
    p_type = format_definition.get("portal_type", None)
    if not p_type:
        return

    form = format_definition.get("form", "")
    if not form:
        logger.info("Param 'form' for portal type {} not set [SKIP")
        return

    logger.info("Applying format '{}' for {}".format(form, p_type))
    ids = list()
    for record in bs.getIDFormatting():
        if record.get("portal_type", "") == p_type:
            continue
        ids.append(record)
    ids.append(format_definition)
    bs.setIDFormatting(ids)


def setup_catalogs(portal):
    """Setup patient catalogs"""
    # setup_core_catalogs(portal, catalog_classes=CATALOGS)
    setup_other_catalogs(portal, indexes=INDEXES, columns=COLUMNS)


def update_client_allowed_types(portal):
    # Allow to add "License" objects inside Client.
    pt = api.get_tool("portal_types", context=portal)
    fti = pt.get("Client")
    allowed_types = fti.allowed_content_types
    if "Location" not in allowed_types:
        fti.allowed_content_types = allowed_types + ("Location",)


def remove_client_allowed_types(portal):
    pt = api.get_tool("portal_types", context=portal)
    fti = pt.get("Client")
    allowed_types = fti.allowed_content_types
    if "Location" in allowed_types:
        allowed_types.remove("Location")
        logger.info("Remove Location from Client's allowed types")
        fti.allowed_content_types = allowed_types


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "senaite.locations:uninstall",
        ]
