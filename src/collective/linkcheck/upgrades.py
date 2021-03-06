from .interfaces import ISettings
from BTrees.IIBTree import IISet
from Products.CMFCore.utils import getToolByName
from logging import getLogger
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

PROFILE_ID = 'profile-collective.linkcheck:default'
logger = getLogger("collective.linkcheck")


def upgrade_tool(tool):
    site = tool.aq_parent
    tool = getToolByName(site, 'portal_linkcheck')

    queue = tool.queue
    checked = tool.checked

    # Initialize datastructures.
    tool.__init__(tool.id)

    # Migrate checked items.
    i = -1

    def t(paths):
        return IISet(
            filter(None, map(tool.index.get, paths))
            )

    for i, href in enumerate(checked):
        entry = checked[href]
        tool.checked[i] = entry[0], entry[1], t(entry[3])
        tool.index[href] = i
        tool.links[i] = href

    tool.counter = i + 1

    # Migrate queue.
    for href in queue:
        tool.enqueue(href)

    registry = getUtility(IRegistry)
    registry.registerInterface(ISettings)


def update_registry(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runImportStepFromProfile(PROFILE_ID, 'plone.app.registry')

    registry = getUtility(IRegistry)
    settings = registry.forInterface(ISettings, check=False)
    if not hasattr(settings, "report_urls_count"):
        settings.report_urls_count = 20
    logger.info("Updated registry entries")
