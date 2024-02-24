# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
import os         

from resources.lib import TheMovieDB as tmdb
from resources.lib.WindowManager import wm

from kodi65 import imagetools
from kodi65 import addon
from kodi65 import utils
from kodi65 import ActionHandler

from .DialogVideoInfo import DialogVideoInfo

ID_LIST_SIMILAR = 150
ID_LIST_SEASONS = 250
ID_LIST_NETWORKS = 1450
ID_LIST_STUDIOS = 550
ID_LIST_CERTS = 650
ID_LIST_CREW = 750
ID_LIST_GENRES = 850
ID_LIST_KEYWORDS = 950
ID_LIST_ACTORS = 1000
ID_LIST_VIDEOS = 1150
ID_LIST_IMAGES = 1250
ID_LIST_BACKDROPS = 1350

ID_BUTTON_BROWSE = 120
ID_BUTTON_OPENLIST = 6002
ID_BUTTON_RATED = 6006

ch = ActionHandler()

dirname1 = "special://home/addons/script.artwork.dump/"
dirname2 = "special://home/addons/script.artwork.beef/"

class DialogTVShowInfo(DialogVideoInfo):
    TYPE = "TVShow"
    TYPE_ALT = "tv"
    LISTS = [(ID_LIST_SIMILAR, "similar"),
             (ID_LIST_SEASONS, "seasons"),
             (ID_LIST_NETWORKS, "networks"),
             (ID_LIST_STUDIOS, "studios"),
             (ID_LIST_CERTS, "certifications"),
             (ID_LIST_CREW, "crew"),
             (ID_LIST_GENRES, "genres"),
             (ID_LIST_KEYWORDS, "keywords"),
             (ID_LIST_ACTORS, "actors"),
             (ID_LIST_VIDEOS, "videos"),
             (ID_LIST_IMAGES, "images"),
             (ID_LIST_BACKDROPS, "backdrops")]

    def __init__(self, *args, **kwargs):
        super(DialogTVShowInfo, self).__init__(*args, **kwargs)
        data = tmdb.extended_tvshow_info(tvshow_id=kwargs.get('tmdb_id'),
                                         dbid=kwargs.get('dbid'))
        if not data:
            return None
        self.info, self.lists, self.states = data
        if not self.info.get_info("dbid"):
            self.info.set_art("poster", utils.get_file(self.info.get_art("poster")))
        self.info.update_properties(imagetools.blur(self.info.get_art("poster")))

    def onInit(self):
        self.get_youtube_vids("%s tv" % (self.info.get_info("title")))
        super(DialogTVShowInfo, self).onInit()
        super(DialogTVShowInfo, self).update_states()

    def onClick(self, control_id):
        super(DialogTVShowInfo, self).onClick(control_id)
        ch.serve(control_id, self)

    def set_buttons(self):
        self.set_visible(ID_BUTTON_BROWSE, self.get_info("dbid"))
        self.set_visible(ID_BUTTON_OPENLIST, self.logged_in)
        self.set_visible(ID_BUTTON_RATED, True)

    @ch.click(ID_BUTTON_BROWSE)
    def browse_tvshow(self, control_id):
            dbid = self.info.get_info("dbid")
            if dbid:
                self.exit()
                xbmc.executebuiltin("Dialog.Close(all)")
                xbmc.executebuiltin("ActivateWindow(videos,videodb://tvshows/titles/%s/,return)" % self.info.get_info("dbid"))
            else:
                self.exit()
                url = 'plugin://plugin.video.themoviedb.helper/?info=seasons&amp;tmdb_id='+ str(self.info['id']) +'&amp;tmdb_type=tv'
                xbmc.executebuiltin("Dialog.Close(all)")
                xbmc.executebuiltin('ActivateWindow(videos,%s,return)' % url)

    @ch.click(ID_LIST_SEASONS)
    def open_season_dialog(self, control_id):
        info = self.FocusedItem(control_id).getVideoInfoTag()
        wm.open_season_info(tvshow_id=self.info.get_property("id"),
                            season=info.getSeason(),
                            tvshow=self.info.get_info("title"))

    @ch.click(ID_LIST_STUDIOS)
    def open_company_info(self, control_id):
        filters = [{"id": self.FocusedItem(control_id).getProperty("id"),
                    "type": "with_companies",
                    "label": self.FocusedItem(control_id).getLabel()}]
        wm.open_video_list(filters=filters)

    @ch.click(ID_LIST_KEYWORDS)
    def open_keyword_info(self, control_id):
        filters = [{"id": self.FocusedItem(control_id).getProperty("id"),
                    "type": "with_keywords",
                    "label": self.FocusedItem(control_id).getLabel()}]
        wm.open_video_list(filters=filters)

    @ch.click(ID_LIST_GENRES)
    def open_genre_info(self, control_id):
        filters = [{"id": self.FocusedItem(control_id).getProperty("id"),
                    "type": "with_genres",
                    "label": self.FocusedItem(control_id).getLabel()}]
        wm.open_video_list(filters=filters,
                           media_type="tv")

    @ch.click(ID_LIST_NETWORKS)
    def open_network_info(self, control_id):
        filters = [{"id": self.FocusedItem(control_id).getProperty("id"),
                    "type": "with_networks",
                    "label": self.FocusedItem(control_id).getLabel()}]
        wm.open_video_list(filters=filters,
                           media_type="tv")

    def get_manage_options(self):
        options = []
        if os.path.exists(xbmc.translatePath(dirname1)):
            options.append(("Artwork dump", "Addon.OpenSettings(script.artwork.dump)"))
        if os.path.exists(xbmc.translatePath(dirname2)):
            options.append(("Artwork beef", "Addon.OpenSettings(script.artwork.beef)"))
        options.append((addon.LANG(1049), "Addon.OpenSettings(script.extendedinfo)"))
        return options

    @ch.click(ID_BUTTON_OPENLIST)
    def open_list(self, control_id):
        index = xbmcgui.Dialog().select(heading=addon.LANG(32136),
                                        list=[addon.LANG(32144), addon.LANG(32145)])
        if index == 0:
            wm.open_video_list(media_type="tv",
                               mode="favorites")
        elif index == 1:
            wm.open_video_list(mode="rating",
                               media_type="tv")

    @ch.click(ID_BUTTON_RATED)
    def open_rated_items(self, control_id):
        wm.open_video_list(mode="rating",
                           media_type="tv")

    def update_states(self):
        xbmc.sleep(2000)  # delay because MovieDB takes some time to update
        info = tmdb.get_tvshow(tvshow_id=self.info.get_property("id"),
                               cache_days=0)
        self.states = info.get("account_states")
        super(DialogTVShowInfo, self).update_states()
