import collections
from bika.lims import api
from bika.lims.permissions import AddSamplePoint
from bika.lims.utils import get_link
from senaite.app.listing import ListingView
from senaite.core.catalog import SETUP_CATALOG
from senaite.samplepointlocations import _
from senaite.samplepointlocations import logger


class SamplePointLocationView(ListingView):
    def __init__(self, context, request):
        super(SamplePointLocationView, self).__init__(context, request)
        logger.info("SamplePointLocationView: init")
        self.catalog = SETUP_CATALOG
        path = api.get_path(self.context)
        self.contentFilter = dict(
            portal_type="SamplePoint", sort_on="created", path={"query": path}
        )
        self.form_id = "locations"

        self.context_actions = {
            _("Add"): {
                "url": "++add++SamplePoint",
                "permission": AddSamplePoint,
                "icon": "++resource++bika.lims.images/add.png",
            }
        }

        self.icon = "{}/{}/{}".format(
            self.portal_url, "/++resource++bika.lims.images", "sampletype_big.png"
        )

        self.title = "Sample Points"
        self.description = self.context.Description()
        self.show_select_column = True

        self.columns = collections.OrderedDict(
            (
                ("location_id", dict(title=_("ID"), index="getId")),
                ("location_title", dict(title=_("Title"), index="Title")),
            )
        )

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "transitions": [
                    {"id": "deactivate"},
                ],
                "columns": self.columns.keys(),
            },
            {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {"is_active": False},
                "transitions": [
                    {"id": "activate"},
                ],
                "columns": self.columns.keys(),
            },
            {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item["replace"]["location_id"] = get_link(
            href=api.get_url(obj), value=obj.getId()
        )
        item["replace"]["location_title"] = get_link(
            href=api.get_url(obj), value=obj.Title()
        )
        return item
