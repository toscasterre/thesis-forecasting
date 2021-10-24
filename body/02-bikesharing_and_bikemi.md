---
jupytext:
  formats: notebooks///ipynb,body///md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.10.3
kernelspec:
  display_name: Bike Sharing Forecasting
  language: python
  name: bikemi
---

# Sharing Services: History and Challenges

+++

## A Brief History of Bike Sharing Services

+++ {"citation-manager": {"citations": {"13h1a": [{"id": "7765261/MVUBY4JD", "source": "zotero"}], "19mvq": [{"id": "7765261/LFMZYHVY", "source": "zotero"}], "2vaa6": [{"id": "7765261/DNETG943", "source": "zotero"}], "429mk": [{"id": "7765261/6TJJ379L", "source": "zotero"}], "6y8i8": [{"id": "7765261/MVUBY4JD", "source": "zotero"}], "8baaa": [{"id": "7765261/MVUBY4JD", "source": "zotero"}], "atco8": [{"id": "7765261/RS2BGLYQ", "source": "zotero"}], "iqk87": [{"id": "7765261/DNETG943", "source": "zotero"}], "is94k": [{"id": "7765261/Q8QH45IB", "source": "zotero"}], "mq8un": [{"id": "7765261/UV5CIHVI", "source": "zotero"}], "nxdy6": [{"id": "7765261/DNETG943", "source": "zotero"}], "xemy5": [{"id": "7765261/6TJJ379L", "source": "zotero"}], "ya8cq": [{"id": "7765261/UV5CIHVI", "source": "zotero"}], "yrbre": [{"id": "7765261/DNETG943", "source": "zotero"}]}}, "tags": []}

The concept behind bike sharing systems (BSS) has been around since at least the 1960 <cite id="6y8i8">(DeMaio, 2009)</cite>. Perhaps unsurprisingly, the first BSS operator was Dutch: it was called Witte Fietsen, or White Bikes, and was deployed in Amsterdam, 1965. The bikes for the sharing service were painted in white, in order to distinguish them from private bicycles, and were made freely available with no locks. Even less surprisingly, "the total absence of security mechanisms led to theft and vandalism, and a rapid demise of Witte Fietsen", as pointed out by Fishman <cite id="yrbre">(Fishman, 2016)</cite>.

Since this failed attempt, researchers have identified three further generations of bike sharing systems <cite id="mq8un">(Parkes et al., 2013)</cite>, along the lines of their technological improvements. Being one of a kind, Witte Fietsen was basically the only representative of the first generations of bike sharing systems. According to DeMaio, the so-called second generation of bike sharing system was launched in the 1990s, in Denmark (1991 and 1993) and subsequently in the Netherlands (1995). These systems were designed with better insurances against frequent usage, as well as vandalism: "The Copenhagen bikes were specially designed for intense utilitarian use with solid rubber tires and wheels with advertising plates, and could be picked up and returned at specific locations throughout the central city with a coin deposit" <cite id="8baaa">(DeMaio, 2009)</cite>. These incentives were not enough, as the time was not yet prime for better customer identification technologies as well as tracking systems.

New features such as "electronically-locking racks or bike locks, telecommunication systems, smart-cards, mobile phone access, and on-board computers" became the norm since 1996, following the example of services such as Bikeabout, developed by Portsmouth University in the United Kingdom <cite id="13h1a">(DeMaio, 2009)</cite>. With Bikeabout, students could use a magnetic stripe card to rent a bike. Since then, a couple of third-generation bike sharing services launched every year across Europe, such as in France (Rennes, 1998) and Germany (Munich, 2000). These services managed to deter theft with "dedicated docking stations (in which bicycles are picked up and returned), as well as automated credit card payment and other technologies to allow the tracking of the bicycles" <cite id="2vaa6">(Fishman, 2016)</cite>. The peak of the third generation was reached around the second half of the 2000s, when Velo'v and its 1500-bike fleet were launched in Lyon in 2005, followed by the 7000 bikes deployed by Velib in 2007 in Paris.

Since then, bike-sharing spread to the rest of the world, and around the first half of the 2010s China established itself as a leader. In 2014, the global bike-sharing fleet was estimated at almost one million bicycles, three fourths of which where in China <cite id="nxdy6">(Fishman, 2016)</cite>; the country also had more than double the number of bike-sharing systems (237) compared to Italy (114) and Spain (113), while there were only 54 in the USA <cite id="iqk87">(Fishman, 2016)</cite>. China is now the leader in sharing services, followed by Europe - which today still maintains its lead over the US, where "the adoption process it at an earlier stage and is gaining momentum" <cite id="ya8cq">(Parkes et al., 2013)</cite>. 

This ongoing surge in popularity is once again due to technological breakthroughs: the fourth generation of bike sharing services exploits the Global Positioning System (GPS) and smartphones to deploy fleets of dock-less (or flee-floating) bikes and e-bikes. China could establish itself as leader also thanks to the rise of mobile technology and apps like WeChat, which was launched in 2011 and quickly became the most used platform in the country: "By the end of 2015, WeChat had 762 million monthly active users worldwide, and roughly 91% of them were from China; moreover, around 639 million users accessed WeChat on a smartphone" <cite id="atco8">(Chen, 2017)</cite>. WeChat is ubiquitous in China and living without it nigh impossible <cite id="is94k">(“In Cina vivere senza WeChat è complicato,” 2018)</cite> - as the platform supports cash transfers and is used for shopping, tipping and paying services.

These new technologies drastically lowered the entrance barriers and the otherwise high upfront investments to set up a bike sharing network. One of the most popular BSS, ofo, was born in 2014 thanks to a collective of students at China's Peking University, who realised they could use the GPS on user's phone to track the bikes. They chose the name "ofo" because word itself resembled a biker and brought together some 2000 bikes to use on-campus<cite id="429mk">(Schmidt, 2018)</cite>. The service was so popular that they quickly made it into a company.

According to Samantha Herr, executive director of the North American Bikeshare Association in Portland, Maine, "large-scale venture capital and cheaper equipment are the game changers that propelled the explosive growth of dockless companies like Mobike and ofo". Dockless bikes are of "lower quality than their docked counterparts" and do not require expensive technologies to interface with a docking station: "That makes them cheaper to mass produce and drop off in new markets" <cite id="xemy5">(Schmidt, 2018)</cite>. It is not by chance that most free-float BSS are completely private, while docked systems almost always feature a partnership between the private sector and local administrations.

Today, according to the estimates on the website [Bike Sharing World Map](https://bikesharingworldmap.com/) <cite id="19mvq">(<i>The Meddin Bike-Sharing World Map</i>, 2021)</cite>, there appear to be almost 1900 bike sharing services in the world, with almost 1000 that have closed down and 300 to be opened. According to an interview to Russell Meddin, the website founder, in 2018 there were 16 to 18 million free-float bikes, plus 3,7 million docked bikes.

+++

## Challenges of Dockless BSS

+++



+++ {"citation-manager": {"citations": {"zyaj8": [{"id": "7765261/5BMQM3AD", "source": "zotero"}]}}, "tags": []}

> The operator-based reallocation problem is known as a Pickup and Delivery Problem (PDP). The application of this optimization problem to BSSs has recently attracted the interest of many researchers and practitioners in this field. It can be modeled by a dynamic or a static approach (Chemla et al., 2013b). In the static version, which is usually performed during the night (when the system is closed, or the bike demand is very low), a snapshot of the number of bikes in each zone is considered and utilized to plan the redistribution. On the other hand, the dynamic relocation is performed during the day when the status of the system is rapidly changing and takes into account the real-time usage of the BSS. In the dynamic case, the relocation plan is strongly supported by forecasting techniques. <cite id="zyaj8">(Caggiani et al., 2018)</cite>

+++ {"citation-manager": {"citations": {"5bab8": [{"id": "7765261/FIPJ84KM", "source": "zotero"}]}}, "tags": []}

> This has traditionally been accomplished through univariate time series prediction using various techniques such as (seasonal) autoregressive integrated moving average ([S]ARIMA, Williams and Hoel 2003) models, artificial neural networks (Dougherty and Cobbett 1997; van Lint et al. 2005), support vector regression (Wu et al. 2004), Kalman filtering (Liu et al. 2006) and non-parametric regression (Smith et al. 2002) among others. Vlahogianni et al. (2004) provide a good overview. More recently, researchers have begun to develop space–time models for traffic forecasting. Various statistical methods for modelling space–time data have been proposed over the years, including multivariate autoregressive integrated moving average [(M)ARIMA] models, space time autoregressive integrated moving average (STARIMA) models (Pfeifer and Deutsch 1980) and variants (STAR models, STMA models), three-dimensional geostatistical models and spatial panel data models, of which Griffith (2010) provides an overview. <cite id="5bab8">(Cheng et al., 2012)</cite>

+++

## The Elephant on the Sidewalk: Electric Scooters

+++ {"citation-manager": {"citations": {"7febn": [{"id": "7765261/H4RXQQ8R", "source": "zotero"}], "8i59d": [{"id": "7765261/AHAU5WIN", "source": "zotero"}], "bkhe6": [{"id": "7765261/BUI6HN97", "source": "zotero"}], "dvvlh": [{"id": "7765261/SAYXS4UZ", "source": "zotero"}], "foag5": [{"id": "7765261/EPW29CK5", "source": "zotero"}], "hnnio": [{"id": "7765261/GVEPNMR5", "source": "zotero"}], "jsywb": [{"id": "7765261/G3F5S8ZS", "source": "zotero"}], "l0la9": [{"id": "7765261/9IRMHVZB", "source": "zotero"}], "vb4td": [{"id": "7765261/F7WYHN86", "source": "zotero"}]}}, "tags": []}

Nowadays, bike sharing systems contend roads (and sidewalks) with new competitors: electrical scooters (ES) have become surprisingly popular across the globe in recent years, displaying a stronger growth trend and adoption compared to BSS. The literature on the history of e-scooters services is still quite young, but some authors trace the beginning of ESS to 2017 <cite id="8i59d">(Christoforou et al., 2021)</cite>. 

Since the last decade, bike sharing must be understood as a piece of two bigger and growing trends: sharing economy and micromobility. The sharing economy is - in economic terms - a new business paradigm focusing on access to exclusive goods, rather than ownership. Before the 2020 COVID Pandemic <cite id="dvvlh">(“La crisi della sharing economy,” 2020)</cite>, sharing economy was also considered a gold mine: in 2017, Bloomberg wrote a long report about the success AirBnB and Uber, the two businesses that embody the idea of sharing economy <cite id="7febn">(Stone, 2017)</cite>. At the time, AirBnB was valued at 30 billion dollars and Uber was valued at almost 70 billion dollars, while both of the companies were still private. The two sharing economy champions went public, albeit with different fortunes, in 2020 <cite id="bkhe6">(“La quotazione in borsa di Airbnb è stata un successo,” 2020)</cite>, and in 2019 <cite id="hnnio">(“Nel primo giorno di quotazione in borsa, le azioni di Uber hanno perso il 7,6 per cento,” 2019)</cite>.

Sharing economy partially overlaps with micromobility.

Provide an exact definition of sharing economy is not straight forward. As of today, some of the most visionary claims about the revolutionary impact of sharing economy have been scaled down - when not outright debunked - and some of its discriminatory and distortionary impacts are being addressed <cite id="l0la9">(“Airbnb Urges Housing Reform in Berlin after Court Overturns Permit Rejection,” 2017)</cite>, <cite id="foag5">(“La nuova sentenza europea sugli affitti brevi,” 2020)</cite>, <cite id="jsywb">(“Le città europee contro gli affitti brevi,” 2021)</cite>.

While attempts have been made <cite id="vb4td">(Trenz et al., 2018)</cite>, we are not interested in taking sides. Sharing economy is of our interest insofar as a macro trend - i.e. a growing and often unstable environment, where players display a great degree of heterogeneity and, for this reason, can suddenly enter or drop out of a market. In the sharing economy, players adopt different business models. Generally speaking, most of these activities involve an ag

+++

## History of BikeMi and Literature Review

+++ {"citation-manager": {"citations": {"42mvi": [{"id": "7765261/RZW74C9X", "source": "zotero"}], "en9lq": [{"id": "7765261/VTA4UCWW", "source": "zotero"}], "riaxh": [{"id": "7765261/RZW74C9X", "source": "zotero"}]}}, "tags": []}

> As expected, it was observed that the service is extensively used for commuting to work-related activities. Regular users compose a large part of the BSS community making use of the service mostly during weekdays. In addition, it was noted that only 'strong' meteorological conditions can impact the use of the service. <cite id="en9lq">(Toro et al., 2020)</cite>

> The BikeMi PSBS started in November 2008 and was the first privately managed bike shared
system introduced in Italy.   BikeMi today has 320 stations distributed in the key points of the city and 5430 bicycles (4280 classic bicycles 1000 e-bikes and 150 pedal-assisted bicycles with child seat) (bikemi website)

> We chose the “Bastioni” area since it corresponds to the traffic restricted zone introduced in
Milan since January 2008. <cite id="42mvi">(Saibene &#38; Manzi, 2015)</cite>

> Predicting variables chosen to explain the counts variability are: (i) the presence of a railway
station in the vicinity (1 if present, 0 otherwise); (ii) the number of underground lines; (iii) the
number of bus lines; (iv) the number of tram lines; (v) the distance in Km from Duomo
square; (vi) the suburb location (1=Northern area; 0=Southern area). <cite id="riaxh">(Saibene &#38; Manzi, 2015)</cite>

+++



+++

## Metriche

+++

Caggiani: MSE
