# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


#=================================================================================
class LocationWidget(widgets.Input):
    class Media:
        js = (
            'http://maps.google.com/maps?file=api&v=2&key=%s' % settings.GOOGLE_API_KEY,
        )

    def __init__(self, *args, **kwargs):
        self.map_width = kwargs.get("map_width", "100%")
        self.map_height = kwargs.get("map_height", "320px")
        self.inner_widget = widgets.HiddenInput()
        super(LocationWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        if value != None:
            a, b = value.split(',')
            lat, lng = float(a), float(b)
        else:
            return mark_safe(_("No location specified !"))
        
        jsname = name.replace("-", "_")
        
        js = '''
<script type="text/javascript">
  (function($) {
    $(document).ready(function() {
      var map_%(jsname)s = null;
      if (GBrowserIsCompatible())
      {
          function savePosition_%(jsname)s(point)
          {
            $("id_%(name)s").val(point.lat().toFixed(6) + "," + point.lng().toFixed(6));
            map_%(jsname)s.panTo(point);
          }

          map_%(jsname)s = new GMap2(document.getElementById("map_%(name)s"));
          map_%(jsname)s.removeMapType(G_HYBRID_MAP);
          map_%(jsname)s.addControl(new GSmallMapControl());
          map_%(jsname)s.addControl(new GMapTypeControl());

          // set center
          var point = new GLatLng(%(lat)f, %(lng)f);
          map_%(jsname)s.setCenter(point, 8);
          
          // add marker overlay
          m = new GMarker(point, {draggable: true});
          GEvent.addListener(m, "dragend", function() {
                  point = m.getPoint();
                  savePosition_%(jsname)s(point);
          });
          map_%(jsname)s.addOverlay(m);

          // save coordinates on clicks
          GEvent.addListener(map_%(jsname)s, "click", function (overlay, point) {
              savePosition_%(jsname)s(point);
              map_%(jsname)s.clearOverlays();
              m = new GMarker(point, {draggable: true});
              GEvent.addListener(m, "dragend", function() {
                  point = m.getPoint();
                  savePosition_%(jsname)s(point);
              });
              map_%(jsname)s.addOverlay(m);
          });
      }
    });
  }(django.jQuery));
</script>
        ''' % dict(name=name, jsname=jsname, lat=lat, lng=lng)
        html = self.inner_widget.render("%s" % name, "%f,%f" % (lat,lng), dict(id='id_%s' % name))
        html += '<div id="map_%s" class="gmap" style="width:%s; height:%s"></div>' % (name, self.map_width, self.map_height)
        return mark_safe(u"%s %s" % (html, js))


#==============================================================================
class LocationField(models.CharField):
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('null', True)
        kwargs.setdefault('blank', True)
        kwargs.setdefault('max_length', 200)
        super(LocationField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = LocationWidget
        return super(LocationField, self).formfield(**kwargs)

    def to_python(self, value):
        if value:
            a, b = value.split(',')
            lat, lng = float(a), float(b)
            return "%f,%f" % (lat, lng)
        else:
            return None
