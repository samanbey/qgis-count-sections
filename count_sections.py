"""
Slice overlapping polylines to segments, 
counting the number of overlapping lines for each segment.
Can be used for visualisations like "all roads lead to Rome"

© 2025, Gede Mátyás
MIT License
"""

import time
t0=time.time()

l=iface.activeLayer()
# TODO: check if it is a line layer.

fields=QgsFields()
fields.append(QgsField("_count",QVariant.Int))


# copy features to a list
feats = []
for i,f in enumerate(l.getFeatures()):
    # DEBUG: copy the first 100 lines only
    #if i>=200: 
    #    break
    f2=QgsFeature(fields)
    f2.setGeometry(f.geometry())
    f2.setAttributes([1])
    feats.append(f2)

# here comes the important part
print('Initially',len(feats),' lines')
nd=0
i=0
while i<len(feats):
    g1=feats[i].geometry()
    if g1.length()<=0:
        # remove zero-length lines without increasing 'i'
        del feats[i]
        nd+=1
        continue
    j=i+1
    while j<len(feats):
        g2 = feats[j].geometry()
        if g2.length()<=0:
            # remove zero-length lines without increasing 'j'
            del feats[j]
            nd+=1
            continue
        isc = g1.intersection(g2)
        if 'LineString' in QgsWkbTypes.displayString(isc.wkbType()) and isc.length()>0:
            f=QgsFeature(fields)
            f.setGeometry(isc)
            f.setAttributes([feats[i]['_count']+feats[j]['_count']])
            feats.append(f)
            f1g=g1.difference(isc)
            f2g=g2.difference(isc)
            feats[i].setGeometry(f1g)
            feats[j].setGeometry(f2g)
            g1=f1g
        j+=1
    i+=1
    
print('After: ',len(feats),' lines')
print('Deleted:',nd)
lines = QgsVectorLayer("MultiLineString","aggregated line sections","memory")
lines.startEditing()
pr = lines.dataProvider()
pr.addAttributes(fields)
pr.addFeatures(feats)
lines.commitChanges()
QgsProject.instance().addMapLayer(lines) 
t1=time.time()
print('Elapsed time: %.1fs'%(t1-t0))
