Title: Dashboard Design UX Patterns Best Practices - Pencil & Paper

URL Source: http://www.pencilandpaper.io/articles/ux-pattern-analysis-data-dashboards

Published Time: Fri, 19 Sep 2025 19:10:50 GMT

Markdown Content:
Whether it’s for analytical, operational or strategic purposes, being able to interpret the right information at a glance is pivotal for teams and departments of all sizes. When designing a data dashboard for your own enterprise product, your team needs to be very intentional about what data points get showcased. Make no mistake, data dashboard UX is tricky, but hopefully we can help. In this article we’ll share the dashboard design UX best practices we’ve learned over the years.

Why does dashboard design matter?
---------------------------------

A product’s dashboards* serve a critical purpose in exposing key data and actionable insights – effectively exposing what’s under the hood in a way that’s useful. With data and by extension AI, being more and more relevant in our modern world, dashboards serve to extend the possibilities of what can be achieved through our use of software.

***dashboards** – the term dashboards is often synonymous with the concept of a homepage in an application or even any experience where there is a sprinkle of data vis (to an entire user experience centred around data and information).

In this article we attempt to lay out the types of dashboards and identify them as different types of experiences, at any rate, make sure you clarify with the team you're working with what "the dashboard"actually is that everyone is talking about.

Why are dashboards relevant to enterprise software?
---------------------------------------------------

In data-heavy platforms, a common pain point is navigating multiple data sources and disjointed systems. Dashboards can unite those systems together and provide a global overview. Dashboards offer an at-a-glance snapshot and prevent users from having to check 10,000 screens just to “know what’s up”. In summary:

*   ⭐ They amalgamate multiple data sources to give us a clearer picture of what’s going on
*   ⭐ They visualize data so we can sense the dynamics between different things
*   ⭐ They are typically quite efficient representations of systems which helps to manage things

Dashboards are challenging
--------------------------

To be crystal clear, designing excellent dashboards is a very complex process which is super difficult to get right, even when you’re using all the best UX practices. There are a lot of barriers and parts that make it difficult. To name a few:

*   **Data-wise** – It’s difficult to understand the data model and the state of the data in its entirety – this is especially true when data varies from customer to customer – this means that you need to protect for a lot of edge cases
*   **User testing** – in our experience, we’ve had some difficulty with conducting user testing with figma prototypes, because the data we fudge doesn’t really reflect the participants dataset, so recognizing issues with it is a much higher cognitive lift. Alternatively pairing with developers to build stuff if you have a setup like that where tapping into real data is possible, that’s ideal. It doesn’t protect necessarily for the data-similarity issue, but it does made the visualizations more realistic overall which can really help improve the user testing insights
*   **Technical challenges** – Using out-of-the-box libraries is very typical for dashboards, which is often the only realistic approach to take as an org. With that, inevitably there are things that aren’t possible and unexpected constraints you didn’t know would show up…. You know gotchas!
*   **Performance** – sometimes the experience is undermined by performance drama, where these massive datasets need to do a ton of computing on the fly or it’s just difficult to render things on the front end, giving you a choppy feeling as you navigate things

If you’re working on any data-rich experience check out our [Data Mapping Workshop](https://www.pencilandpaper.io/product/enterprise-data-mapping-workshop) (it's our secret weapon to making great dashboards, filters and tables!)

Things to consider for your dashboard UX design
-----------------------------------------------

Follow these prompts along with your team as you embark on tackling your dashboard UX design. These prompts should help you think about how you want to apply dashboard best practices to your specific scenario.

**Is the data clean enough?**The very first thing you get to do is a data architecture analysis. Sounds fancy? But really, just sit down with your _brainiest_ peeps, look at your data structure, have a chat with your DBA. What data do you even have? Is the data maintainable? Is the metadata consistent and scalable? Start with prompts like these:

*   Is the data tracked over time?
*   How much historical data do we have? (years, months etc)
*   Can we calculate if/when statements to create insights?

**Map out user context**As much as it would be nice to design a dashboard for each persona, that wouldn’t be very efficient. Find the overlaps and divergences.

If the divergences are small enough, creating multiple unique versions might not be necessary. But if they are large, you should consider catering to separate personas.

Aim to keep it global at first (default state) + allow for granularity with interactions (see below).

**Uncover the data structure and details**

Work with a data expert to answer the right questions early in the process. Interestingly, the details here matter and there's a set system you can follow to uncover those vital details - saving time and surprises down the road. Our [Data Mapping Workshop](https://www.pencilandpaper.io/product/enterprise-data-mapping-workshop) outlines a foolproof and efficient process for doing just this!

✅ 📊 Eliminate the difficulty by 50%

Over and over, we found ourselves having bit "gotchas"when designing dashboards, filters, tables - anything "data-ish" - all because we found out key info late in the process. We created a system that solves for that. Dig in and discover more about our [Data Mapping Workshop](http://www.pencilandpaper.io/articles/ux-pattern-analysis-data-dashboards#), you'll thank yourself later!

**Determine dashboard design goals**What are users expecting to do with that screen? What questions do they need the dashboard to answer?

*   What needs their attention?
*   What do they need to report on?
*   What deserves a spot on the dashboard?
*   What are the most global metrics that deserve higher visibility?
*   What needs to be visualized?
*   What personas/scenarios does this dashboard need to be catered to?

**Figure out what key actions will be executed there —prioritize warnings and actionable items**In order to offer an experience that is informative at the overview level, you need to be very aware of what users are looking for. You can always allow them to drill down but be sure you surface the key stuff they can take action on, and any warnings they should quickly be made aware of.

**Find out what is taking the most time for users to compile**Try to prioritize which charts will actually make it to the dashboard. For this, you need a good understanding of your typical user personas, what are they currently doing to obtain this information? Of these things, which ones do they do every day? Versus once a month or once a quarter?

To do this, try a workflow mapping exercise with your users, or you can learn a lot by reviewing their internal spreadsheets or reports.

This can help guide the selection process of what to actually show on the dashboard. When personas are very differentiated, this can warrant creating multiple versions of the dashboard.

‍

‍

👀 Have a look at our [Data Mapping Workshop](https://www.pencilandpaper.io/product/enterprise-data-mapping-workshop) to find out more.

Types of dashboard experiences and use cases
--------------------------------------------

Dashboards can be very ‘view only’ or they can be deeply interactive and integrated into how users achieve their goals. At an abstraction level, you can think of a dashboard as a page with some data visualization in there, because they are wildly diverse.

**Reporting**This is a comprehensive or overview content, often serves to amalgamate data all together. Often you see an export function and/or share functionality. The point of it is to tell a story with data.

Ex. quarterly earnings data

**Monitoring**This functions to alert and warn users. This is a more living, breathing type of dashboard, where data may be live and ticking away in realtime. The point of this dashboard is to alert people to problems and anomalies.

Ex. monitoring a fleet of smart devices or web uptime/downtime

**Exploring and discovery**This functions to give users a means to discover data and infer insights. Here, playing with the data, drilling into it, exploring around is the focus. The point of this type of dashboard is to give users flexible means to find out new things.

Ex. Open data experiences like Our World in Data, example [Mental Health](https://ourworldindata.org/mental-health)

**Functional and integrated**This functions to guide users towards where they need to focus. It’s a less urgent version of a monitoring dashboard and might show much less information. The point of this type of dashboard is to show users where they might need to focus.

Ex. a project management tool showing “at risk” tasks in a queue

**Product home page**This functions as a contextual index of sorts. It’s more about giving an overview as well as serving as a navigation, this is super common in enterprise software. The point of this type of dashboard is to give users context before they navigate somewhere.

Ex. a SaaS application for marketing which shows you main sections like leads and sales with totals and deltas

![Image 1](https://cdn.prod.website-files.com/65d32a145451f865e1ca2bbe/668c382adaca9738d41c6dd7_card-data-dashboard-service.png)

Data Dashboard Design Service

Sick of fumbling through iterations and still overwelming and underwelming your users? We work with B2B SaaS companies and others working to deliver great data-rich user experiences. Explore our [Dashboard UX service](https://www.pencilandpaper.io/services/data-dashboard).

Anatomy of dashboard UX
-----------------------

![Image 2: hand-drawn simplified dashboard screens. First one showing a filters area as a left sidebar, navigation as a top bar, and a content area made of sections. Second one showing the zoomed-in content area and separate sections made of modules. Third one showing a zoomed-in module made of data, line chart and key numbers](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1a1b7b5b3eb4b7221d385_Anatomy-v2.png)

Ok friends, here’s where we start to both zoom in AND zoom out on the whole experience of a dashboard. The experience of using a dashboard isn’t just looking at some charts, it involves [interactions](https://www.pencilandpaper.io/articles/microinteractions-ux-interaction-patterns) and key moments during your experience that you need to factor into your dashboard design. We’re applying a lens of the moment-to-moment experience within a dashboard experience, so we can appreciate not JUST the graphs and charts, but everything surrounding them.

### Navigation

**AKA Getting there.** Without getting into the ins and outs of navigation (we’ve written an in-depth article on this topic already for you to peruse). It’s important to appreciate the state of mind and expectations set, prior to the person engaging with your dashboard at all. Don’t forget this part of the journey.

![Image 3: Dashboard with navigation on the left and selected state on the item selected](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1a1b7241e9fc8cb02ad72_Dashboards_Nav.webp)

We recommend:

*   Following [navigation patterns and best practices](https://pencilandpaper.io/articles/ux-pattern-analysis-navigation/) – so that when people reach the dashboard experience they are at an advantage compared to a disadvantage – brain cells shouldn’t be wasted on weird nav, especially when you have data to analyze

### Getting Oriented

**AKA figuring out what you’re looking at.**Upon navigating to the page itself. This is the moment where the user viewing this page does the mental lift of figuring out: what the page is for, what it’s showing me, what it’s meant to do, if they can achieve their task or their goal here or not.

![Image 4: Dashboard with large hero section with a title and description](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1a928723f0d0456718d16_Dashboards_Leadspace.webp)

We recommend:

*   A clear page title – so people can immediately know what the point of the page is overall

*   A clear description of the page – so people can understand what they can do there

![Image 5](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/66b59e3434e130b2d7a26981_65e1a9be000f13ee9277187d_Dashboards_Grouping.webp)

We recommend:

*   Charts and graphs are conceptually grouped together – so that people can understand what should be considered together and separately. When there’s just “a bunch of data” people can feel alienated and disoriented.

![Image 6](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/66b59e3434e130b2d7a2697b_65e1aac89db64df035763ef3_Dashboards_Grouping-1-1.webp)

We recommend:

*   When you’re at that first layer of discovery, you want to help people understand what the chart contains and where it can lead them, so overview type of charts can be a great place to start

*   Defaults are chosen for all your charts which don’t show #allthethings by default which are appropriate for the audience (this is tricky work and key to creating high quality interactions) – just because you have the data, doesn’t mean it should be shown

![Image 7](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/66b59e3434e130b2d7a269a2_65e1ab0216483846b31926fd_Dashboards_Tooltip.webp)

We recommend:

*   Jargon is explained via tooltips and other forms of descriptions – people shouldn’t have to put on their Sherlock Holmes hat and launch an investigation everytime they look at your interface

Don’t forget to include any **loading feedback** and **empty states** that might apply to the page – this can easily be omitted or forgotten, but missing out on this gives your experience the vibe of a rackety chair as opposed to an ergonomic delight with lumbar support, if you catch our drift.

p.s. Are you seeing just how many considerations you need to consider when making a high-quality interactive experience? Yowza. No wonder you’re tired.🍪🛏️

### Filtering and parsing the data

**AKA finding and discovering information**. There’s a lot to the [filtering](https://pencilandpaper.io/articles/filtering-a-data-table-while-editing/) of the data itself, which you’ll need to dig into the UX best practices for and really give it some attention.

![Image 8: Dashboard showing filters on the left with prioritized filter categories](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1ab2defde717f2b8cbf07_Dashboards_Filter-1.png)

We recommend:

*   Prioritize the filters presented by default to be super useful

![Image 9](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/66b59e3434e130b2d7a2697e_65e1ab5a115640d3f9ad3170_Dashboards_Filter-Loading-1.webp)

We recommend:

*   Don‘t forget [loading ux](https://www.pencilandpaper.io/articles/ux-pattern-analysis-loading-feedback/) considerations, it’s key to understanding that the system is working, more details on how to do this in our loading article

‍

### Drilling into information

**AKA Digging deeper.**Drilling further into the information to reveal more detail, reference something or double-check information is an important part of the experience in a dashboard. This is the part where users are free to explore more and discover and really “use” the data. If people want more, that’s usually a good sign.

![Image 10: Dashboard wireframe showing flow of opening overlay drawer or navigating to a details page](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1abcafd61a5053f51fccd_drilling-in-overview.webp)

#### Drawer pattern

This pattern allows a lot of flexible space to present information without having to exit the context you’re currently in.

![Image 11: Dashboard design showing pop out drawer with metadata and actions](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1abca7fac0f75cd246ec9_Dashboards_drawer-2.webp)

#### Details page

This pattern allows you to house a whole bunch of details in an entire view, which in and of itself could have dashboard-like qualities! But let’s not get crazy.

![Image 12: Dashboard design with table view showing totals at the top](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1abca54ac73362c4da592_Dashboards_Details.png)

### Executing actions

**AKA getting tasks done.** Dashboards, like the rest of your software, need to get stuff done. As such, you need to account for this in your dashboard experience. For dashboards, they might have simple interactions, like say an “export” button, for others you might be executing something more complex, say like pushing a software update to specific instances or something like that.

![Image 13: Dashboard design table view showing multi-select rows and action button](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1abca23419047dad7c238_Dashboards_Actions.png)

‍

We recommend:

*   Interaction feedback – use success and error feedback as needed (we suggest brushing up on these patterns)

*   Multi-select – make sure that multiselect interactions are obvious and have appropriate affordances which you can’t miss.Consider if the best way to show feedback is contextualized or more global.

*   Prioritize actions – make the most important the most noticeable and the least important, the least noticeable

*   For multiple actions, they can be housed in a dropdown button (see more on table actions and high quality interactions)

Now that we’ve reviewed dashboard experiences in a holistic way, now it’s time to dig in more into the data visualization, layouts, cards and the like. Let’s go!

‍

Bring in the professionals
--------------------------

Now, if you're a small team and data is central to your experience, it may be obvious at a certain point that incorporating data science, user complexity, interaction design, visual design and user testing all by yourself isn't working, or isn't working fast enough. In a word, you're under-resourced, but the stakes are high and getting your dashboard right is of great consequence to your business.

Even some of the best designers and best data scientists in the world have an enormous challenge of making data make sense. On top of that, user expectations for great data experiences are only increasing. Perhaps it's time to consider shying away from the DIY approach to designing dashboards and call in the rare experts that can get it done. Explore our [data dashboards UX service](https://www.pencilandpaper.io/services/data-dashboard) and see how we can whip your experience into shape in no time.

‍

Layout UI patterns for dashboards
---------------------------------

### Intuitive page layout

Dashboard UX design and UI are very closely related. On such a critical page, you need to optimize content placement for the way your users will scan the page. This key page acts as a homebase with strategic entry points into more granular flows. Users should be able to click a module or chart and enter a dedicated page for that data type.

To optimize that behaviour, consider the typical eye-scanning patterns that are true for web pages. For left-to-right (LTR) language speakers, those would be the F and Z patterns.

The F shape suggests that the eye will naturally get drawn to the top-left corner at first and then scan horizontally, before zig-zagging (that’s the Z) down the page, again starting from left to right for the following sections or rows.

![Image 14: hand-drawn simplified dashboard screen in purple with directional lines in pink starting from #1 in the top left corner, going across to the top right of the page, then diagonally down to #2 middle-left, going towards the right but stopping mid-page, going diagonally down to #3 bottom-left and then a little further to the right](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1ae80edb75043a959dd43_F-Z-Patterns.png)

_Eye-tracking research shows that users tend to scan webpages in “F” and “Z” shapes_

Since the top left area gets more attention, that’s where you want to showcase the most global numbers, or the most relevant data.

You’ll want to structure your charts and graphs into related sections going top-down. Starting of course with the most important at the top, following with a global overview in the middle, and wrapping up with a more detailed breakdown at the bottom.

Research around the F pattern proves that the further down users get on a page, the less they scan the full width of the row. So again, make sure to stick the important stuff on the left side.

### Consistent card layout

Card layouts are very common for data dashboards and come in many shapes and sizes. A card layout doesn’t mean all your charts are visually enclosed in a distinct “div”. It just means that your charts and graphs are treated the same way, consistently placed along their title, labels, legend and other accessories.

![Image 15: Examples of styles of cards containing title, line chart and legeng: Floating with no background, Card with white background and rounded corners, Title accent with bold full-width coloured line underneath title](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1ae8089785e0ad2b78d49_Not-all-cards-white-BG.png)

You’ll want to study the best way to layout your graphs inside their cards. Make sure you decide on a solution that can allow for different types of graphs, and that leaves room for recurring elements like key values, date pickers and legends.

Here, consistency is key. You’ll help your users a lot if they can quickly find the title on the top left of each module, or the legend always at the bottom center. That’ll help reduce visual noise when they scan the page.

![Image 16: Bar chart, line chart and pie chart, laid out in cards of various sizes all with title in the top left, date picker in the top right, and legend at the bottom](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1ae808ab6f1df8ee1bf48_Consistent-in-card-layout.png)

Chart UX patterns you can use
-----------------------------

Now that you’ve nailed down the page structure that works best for your users and your data, let’s zoom in a little and explore ways to elevate the charts and graphs you present in your dashboard.

Think of it this way: how much _extra love_ do your out-of-the-box graphs deserve? Of course a lot of the patterns mentioned below come for free with your typical chart library but do the work of determining which small tweaks need to be brought to elevate your data and better meet the user needs.

### Use of colour

Smart use of colour is a very elegant way to provide additional meaning to the data. How might we go beyond the basic language of red-yellow-green for bad-neutral-good?

![Image 17: Red colour square Negative, Yellow colour square Neutral, Green colour square Positive](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aeca869559e74ace8b6f_Classic-Stoplight-Formula.webp)

Some of your charts might benefit from a secondary palette like different shades of, say, your brand colour to express levels of intensity. Higher values could indicate larger quantities or densities, and lower values smaller ones.

![Image 18: Rectangular scale of colour samples going from 10 - light purple to 100 - almost black, with Brand Colour being pointed to number 40](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aecad3fe0be412080d07_Colour-Intensity-Scale.webp)

_Using variations of the same colour to represent levels of intensity_

Other classics if your page is already filled with stoplights are blues to indicate positive values, and oranges for negative trends.

![Image 19: sample of three shades of blue and a blue line chart trending up with caption Blues Positive trend. Sample of three shades of orange and an orange line chart trending down with caption Oranges Negative trend](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aeca8d3056d05d788122_Blues-Oranges.webp)

_Blues and oranges provide the same levels of vibrancy and contrast as greens and reds, without your UI feeling like a trading terminal_

When exploring colours, it’s important to keep accessibility in mind. To ensure good visibility, make sure the colours you choose have high enough contrast against your background colour.

### Lines, fills and textures

Again with accessibility in mind, it’s considered best practice not to rely on colour alone. Look for ways to add some hashes or texture in your fills and your legends.

![Image 20: Base colour and variations by adding a dot grid, vertical lines, horizontal lines, line grid, diagonal lines to the right, diagonal lines to the left, diagonal grid](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aeca7c4047bdc4c88a8d_Hashes-Textures.webp)

_We can build a lot of variety from a single base colour_

The same holds true for lines. A line chart with a bunch of solid lines in different colours can quickly become hard to interpret. You can add in a variety of styles of dotted lines.

![Image 21: sample of various dotted line styles: dots, dashes, wider gaps, dashes & dots, variable dash length, solid](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aecaaf47bb1f8e46f00b_Various-Line-Styles.png)

_Increase accessibility with dotted and dashed lines_

‍

> 👋 If this is all ALOT and you've been trying to "just figure it out"with a tiny team, we can help you get a great new version out the door in no time, check out our [UX services](https://www.pencilandpaper.io/services)and [dashboard design services](https://www.pencilandpaper.io/services/data-dashboard)for more info.

‍

### Deltas

Deltas are used to showcase differences (aka: diffs). When relevant, make sure your charts bring forward consistent deltas to your users. They can be relative (% change since same day last month) or absolute (absolute difference compared to global average). Deltas should catch the eye and be quick and easy to make sense of.

![Image 22: collage of various types of deltas: Icon first has a colour indicator red yellow green, an icon trending up flat or down and the percentage change; Textual has a small arrow icon trending up flat or down and a natural language label; Inline is displayed inside a table row with percentage change on top of small coloured dot red green yellow with pale label](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aeca16483846b31bbe5a_Deltas-icons-colours.webp)

_Deltas are either positive, neutral (little to no change), or negative_

A typical way to present deltas in the context of graphs is to allow users to select from a few options.

![Image 23: line chart in a card layout with a delta dropdown in the top right corner where options are selectable: compare to last week, last month, last year, industry](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aecb020d3594cfb562b9_Delta-dropdown.gif)

### Responsiveness

When adapting your dashboard UX design for mobile, the first question to ask is whether all the information is relevant for your users’ “on-the-go” scenarios. Try to understand what they need to see when they’re not sitting at their desk. Chances are they don’t need it all and you’ll save yourself a whole lot of work.

Maybe only display that top section, the most important or global data, and fit it in a vertical layout instead?

![Image 24: stacked bar chart in a horizontal layout where hovering on a colour from one bar highlights the same colour in all bars](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aeca8ad9a3e6af64805e_Hover-across-graph.gif)

_A stacked bar chart in its desktop horizontal version_

![Image 25](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/66b59e3534e130b2d7a269d7_65e1aff458451cded09435e8_Made-vertical-min.gif)

_The same stacked bar chart adapted to a vertical layout for mobile_

![Image 26: mobile dark interface showing a blurred bar chart with white text on top: "this chart is better viewed on a larger screen, try rotating your device into landscape mode"](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aeca23419047dad94c9e_Landscape-mention.webp)

There’s also no harm in indicating that this page or a particular chart is better experienced on a larger screen, or to encourage them to flip their mobile in landscape mode.

### Data labels on charts

In general, labels are central to excellent UX design, dashboard design is no exception. When dealing with large timescales or datasets, negotiating space might become a bit tricky. Angled labels typically work well, but there’s always a limit. You should account for those edge cases early and pre-determine the logic to use once the threshold gets surpassed.

There are different ways to navigate label length. Determine in advance how you want long labels to behave. How many characters can you display without it feeling too bloated? How do you want to manage ellipses to best serve your users? For example, deciding to crop the ending versus the middle of a label? “September 19” truncated to 6 characters can become: “Septem…” or “Sept… 19”; which one conveys the most information?

If space really becomes an issue, remember: not everything has to be visible at all times. The visual of the chart itself should communicate the majority of the insight. So don’t hesitate to hide some labels altogether and leverage tooltips in these denser views where more specific labels could appear only on hover.

![Image 27: line chart showing a lot of x-axis labels one per week and per month and per quarter very dense barely legible](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aeca8d3056d05d78811e_DONT-Too-many-labels.webp)

![Image 28: line chart with fewer x-axis labels shown by default only one label per quarter instead of per month](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aecac66e7fc4b9d92d75_DO-Reduced-labels.webp)

_Here we’ve got one endpoint per week, but only display labels for Quarters to provide the high-level trends & projections_

You can prevent some of these issues by limiting the length of the selectable filters or date range to ensure users can only select as much as the viewport can offer.

Finally, there’s always the option of coding a horizontal scroll. But for this, watch out for where the scrollbar will appear and account for the room it’ll take up!

### Typography & hierarchy

When looking at trendy _dribbbl-y_ dashboards, we often see big bold numbers in a stylish display font. When done well, these typographic accents can really help the functionality of your dashboard. They do a great job at catching the eye. If you’ve done your research and identified the right numbers to accentuate this way, it demonstrates confidence and decisiveness.

![Image 29: dashboard interface with beige background colour and dark green accents where key numbers are shown in a very bold and larger font size](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aecacf0479a6dadf75d9_Big-fancy-numbers.webp)

From the user’s perspective, it means you’ve done your job, you know what your users are looking for and you’ve made sure the system is effectively keeping track of these data points. All-around trust-builder. And karma points.

Interactive graphs and charts
-----------------------------

Okay, now that our charts and graphs are neat and consistent inside their page structure, let’s look at interactions we can offer our users.

To avoid barraging the user with data, you can borrow some of the concepts of progressive disclosure. Offering gentle reveals and visual emphasis upon the user’s request really helps mitigate overwhelm and confusion. Here are a few interactive UX patterns that embrace those principles.

### Tooltips & hover states

Hover states are the perfect way to hide that secondary layer of detail while avoiding visual noise. Since the goal of the dashboard is to provide an at-a-glance snapshot, the visual of bars or lines should be enough for users to sense the trends. But revealing additional detail upon hover is a great use of progressive disclosure. That way your users can leverage it when needed, and it doesn’t clutter the page by default.

![Image 30: Colourful stacked bar chart where hovering on legend items highlights the related colour in each bar](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aeca387ebb2e9372ae91_Legend-Hover.gif)

### Toggling variables

Another interaction that could be relevant for some of your charts is the turning on and off of certain variables. Let’s say the default view of a line chart presents 7 different lines. It might be useful for the user to hide some of those endpoints so they can focus on comparing a smaller selection.

This can be implemented by making your legend items into a checkbox list.

![Image 31: Part of a dashboard screen where deselecting items from a table view affects the number of lines visible in the data chart above](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1aecac2557bdc3b043185_Checkbox-legend.gif)

### Filters within dashboards

In short, you can offer your users a full-page filter sidebar (or horizontal bar for that matter) but this means the filter selection affects the whole page —i.e. every single chart at once. It’s always useful to have filters always accessible; consider a fixed header for users to easily initiate them as they navigate the page.

Another option is to have smaller filter options inside each module or section. That way, users can be specific in what they want to see. They could filter the top section by location, and then select a specific date range for the middle section.

### Custom personalized dashboard pattern examples

Now, if you really want to go all out and you know from your users that the dashboard is where they spend most of their time, you might want to build some customization options.

This can take many shapes. You could allow them to move modules around, and reorganize the order of the sections by drag-and-dropping. (Fancy!) You can also let them hide and show some sections.

You might even want to consider integrating a custom “build your own dashboard” flow in the onboarding UX. That way, they get to explicitly pick the endpoints they want to see and they get to make it as minimal or as complex as they wish.

![Image 32: Jira example of adding gadgets to a new dashboard and rearranging the layout](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1afacfc05a4b49d89abac_Jira-dashboard-builder.gif)

_Example of Jira’s Create Dashboard flow. You get to pick Gadgets and organize them inside a module layout_

‍

Common dashboard UX problems
----------------------------

### Density disjoint problem

The data eyeball attack🫣 – It’s like a wall of text, but make it data. This is where density of the data makes users run for the hills – there’s a lot, and technically it’s impressive, but the density isn’t appropriate for those outside of the role of “data scientist” or “data analyst”. **If there’s some room to integrate a visual break, an extra serving of whitespace or just a little bit less shown by default, why not try it out and see what your crew thinks.📏**

🖇️ More on solutions to this in [Typography & hierarchy](https://pencilandpaper.io/articles/ux-pattern-analysis-data-dashboards/#typography-hierarchy)

### Data seems random and unfocused

This happens when the general attitude on the team is this: We have it, so why not show it? This sounds great in theory, but in practice, this shows serious diminishing returns, as more and more charts serve to destabilize users, as they assume if it’s present, then it must be important. The hard work of information architecture is what actually makes a data dashboard experience great, not the fact that there’s a BUNCH of charts.**Next time you CAN put another chart in, ask yourself, is this going to be really useful? 🧐..AKA ask yourself, does this spark joy?” 😉**

🖇️ More on solutions to this in [Toggling variables](https://pencilandpaper.io/articles/ux-pattern-analysis-data-dashboards/#toggling-variables)

### Comparisons and baselines are lacking

Even with well-designed and used dashboards, you can still get the feedback that “this is just a bunch of data”, which is fair enough. Have you ever tried to estimate story points (in an agile team) without a frame reference around your estimate (1,3,5,8 etc). What about when you compare it to a previous story, it becomes much easier. In the data world, our cognitive landmarks (like average or target numbers) can really help us to gauge where we are and what we’re looking at. **If you get the feedback “this is a lot of numbers”, apply the lens of comparison and see if that helps.🍏🍊**

🖇️ More on approaching solutions to this in [Deltas](https://pencilandpaper.io/articles/ux-pattern-analysis-data-dashboards/#deltas).

![Image 33: Dashboard design example from GA4 without acronym labels](https://cdn.prod.website-files.com/65d605a3b4417479c154329f/65e1afacb597c60b0bbde89a_GoogleAnalytics.webp)

_This is GA4, Google’s new iteration of Analytics. The acronym DAU / MAU is not defined_

‍

### Technical jargon and lack of information

In a feat of irony, one of the most common UX issues is that data is simply shown but not explained in the least. It can be a stretch to even get a title on the page or a graph, let alone a description! On top of that, acronyms are used to shorten things, but explanations in the form of tooltips, legends or other mechanisms are missed. So the user simply sits there, blinking into the abyss. **Next time you create a dashboard, apply the lens of someone with zero context, see if you can turn that vacant stare into a nerdy smile.🥴→ 🤓**🖇️ More on approaching solutions to this in [Tooltips & hover states](https://pencilandpaper.io/articles/ux-pattern-analysis-data-dashboards/#tooltips-hoverstates)

### Colour-coding mishaps

It’s common knowledge that only using colour to indicate the status of something can leave our colour-blind friends in the dark, it’s not considered accessible (especially as the main two colours for good vs bad is red and green *face palm*). Issues around colour coding extend not just around this particular issue, but colour can be overused in data dashboards quite easily without mapping to a particular meaning. When you have various colours within charts themselves, plus status indication, queues for interaction you can get into a situation where you’re suddenly looking at a rainbow salad with nothing sticking out as important. **Next time someone says: yeah let’s just make that box purple, implore your team to see reason and try to describe the convention in words first, then see if it still warrants a colour to be involved. 💜**

🖇️ More on approaching solutions to this in [use of colour](https://pencilandpaper.io/articles/ux-pattern-analysis-data-dashboards/#use-of-colour).

Whether or not you venture into these more advanced interactions, you always want to give your users some options. If ever the way you designed the dashboard doesn’t meet their needs, you should always allow the data to be exported as raw CSV’s so they can pull it out and manipulate it elsewhere. That’s just some basic data etiquette. Data needs to be free! If you love the data, let it go. 🕊

Wrapping up
-----------

This article has touched on a lot of dashboard considerations and design moves you can make, but we're only really scratching the surface of the real complexity in designing experiences like this. Data exploration and understanding is an organic and iterative process for a user. Out there, we're catering to data noobs all the day to data scientists and uber data geeks. This is a wide spectrum of understanding and many of our precious users have a really tough time articulating what's going on in their minds when data is right in front of them.

On top of that, most designers aren't comfortable with data and most data people aren't comfortable with design. So the only way to make a super great experience is to collaborate at an elite level.

Another factor that comes into play is AI and how that integrates into all levels of data exploration. We have use cases for people to get a "specific answer"as well as view and understand trends and anomalies, issues and quirks with the data. WOW.!

So, you've got a meaty task in front of you, but here's some motivation. The more people understand data, the more logical and informed their decisions and perspective can be right? Keep going!
