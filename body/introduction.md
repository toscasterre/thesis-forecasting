---
jupytext:
  formats: notebooks///ipynb,body///md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.0
kernelspec:
  display_name: Deep Learning Forecasting
  language: python
  name: bikemi
---

+++ {"citation-manager": {"citations": {"bbtbg": [], "h8icd": [], "mpxer": [], "nvf0v": [], "ukx8p": [], "z8l1c": []}}, "tags": []}

> As expected, it was observed that the service is extensively used for commuting to work-related activities. Regular users compose a large part of the BSS community making use of the service mostly during weekdays. In addition, it was noted that only 'strong' meteorological conditions can impact the use of the service. <cite id="bbtbg">[NO_PRINTED_FORM]</cite>

> The BikeMi PSBS started in November 2008 and was the first privately managed bike shared
system introduced in Italy. @saibeneBIKEUSAGEPUBLIC  BikeMi today has 320 stations distributed in the key points of the city and 5430 bicycles (4280 classic bicycles 1000 e-bikes and 150 pedal-assisted bicycles with child seat) (bikemi website)

> We chose the “Bastioni” area since it corresponds to the traffic restricted zone introduced in
Milan since January 2008. <cite id="nvf0v">[NO_PRINTED_FORM]</cite>

> Predicting variables chosen to explain the counts variability are: (i) the presence of a railway
station in the vicinity (1 if present, 0 otherwise); (ii) the number of underground lines; (iii) the
number of bus lines; (iv) the number of tram lines; (v) the distance in Km from Duomo
square; (vi) the suburb location (1=Northern area; 0=Southern area). <cite id="z8l1c">[NO_PRINTED_FORM]</cite>

> Sun et al. (2018) investigated the unsuccessful experience of the Pronto programme and found that effects of hilly terrain and the rainy weather were two commonly perceived contributors to the failure. <cite id="h8icd">[NO_PRINTED_FORM]</cite>

Focus on life duration of bike sharing systems <cite id="ukx8p">[NO_PRINTED_FORM]</cite> or the bike allocations (competition) <cite id="mpxer">[NO_PRINTED_FORM]</cite>, as well as methods to promote the sharing services @zhangDynamicPricingScheme2019. We focus on forecasting the number of rentals why?
* numero di bici da spostare, forecast se una stazione è piena o meno
* crescita dei noleggi -> nuove bici da comprare?
* volumi nelle nuove stazioni?
* zone calde forecasting
* idealmente a livello orario?

RIFARE CALCOLO CON TASSO MEDIO DI RIEMPIMENTO ORARIO?
RIDUCE VARIANZA
recuperare numero slot libere per quartiere

* Circoscrivere AREA C
* Numero di quartieri in area c
* numero di stazioni metro e stazioni treni (pullman non significativi) in ciascun quartiere?
