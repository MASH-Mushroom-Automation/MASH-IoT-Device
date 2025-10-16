Project Proposal 
Llanes, Kevin A. 
Antang, Irheil Mae S.
Bae, Ma, Catherine H. 
Failana, Jin Harold A. 
Namias, Jhon Keneth Ryan B.  
Pabua, Emmanuel L. 
Valencia, Ronan Renz T.
BSCS - 4B 

Project Title: 
M.A.S.H. — Mushroom Automation with Smart Hydro-environment using IoT and AI for Sustainable Harvest with E-Commerce for Oyster Mushroom Growing using Flutter, NestJS, Next.js, PostgreSQL, SQLite  and Firebase 

RATIONALE:
The Pleurotus florida, commonly known as white oyster mushroom, is a nutritious and versatile food crop that is relatively easy to cultivate. It can grow on low-cost and widely available substrates such as rice straw, sawdust, or coffee grounds, making it sustainable and suitable for small-scale farming (Rivera et al., 2023). It has a short growth cycle, requires minimal space, and can be harvested within a few weeks. Because of these characteristics, it serves both as a food source and as a potential source of supplementary income for small farmers and households.
White oyster mushrooms are rich in protein, vitamins, and minerals while being low in fat and calories. Studies also indicate that they contain bioactive compounds that may contribute to lowering cholesterol, strengthening the immune system, and improving digestion (Aditya et al., 2024) Environmentally, they provide an efficient means of recycling agricultural waste, help reduce carbon footprint, and produce residual substrates that can be repurposed as fertilizer.
Mushroom production in the Philippines offers strong potential as a sustainable livelihood and food source, yet farmers face persistent obstacles that limit productivity and growth. Mushrooms are highly sensitive to environmental conditions such as temperature, humidity, and light, making them vulnerable to sudden weather changes and high tropical heat that reduce yield and quality. Pests, diseases, contamination, and insect infestation remain major threats, often leading to significant crop losses (Rodriquez, 2024). Many growers still rely on traditional, labor-intensive methods, which increase risks of error and inconsistent harvests due to the lack of modern farming technology. Post-harvest challenges are equally pressing, as mushrooms are highly perishable and most small-scale farmers lack access to proper storage, transport, and distribution systems, resulting in spoilage and unstable income (Quion et al.). Furthermore, limited market connections and dependence on middlemen expose farmers to pricing uncertainties, discouraging long-term growth and investment (Domingo, 2025).
This thesis project proposes the development of M.A.S.H. (Mushroom Automation with Smart Hydro-environment using IoT and AI for Sustainable Harvest), an IoT- and AI-driven system designed to optimize the growing of white oyster mushrooms. Traditionally, a fruiting bag can produce harvest-ready mushrooms consistently for 2–3 months under strict and proper care using small-scale growing methods. Our goal is to enhance this process by making it more efficient, consistent, and sustainable, while extending the productive lifespan of each fruiting bag.
MASH consists of a two-box system. The first box, the IoT-enabled growing chamber, is equipped with a combined sensor module for humidity, carbon dioxide, and temperature, a humidifier for moisture regulation, an exhaust fan, a blower fan for optimal airflow, and an LCD module for real-time status display. This chamber integrates with a mobile application that allows users to monitor environmental conditions, manually adjust system operations, and receive alerts and notifications. In addition, an AI model works alongside the IoT system to analyze sensor data, predict environmental needs, and recommend or automate adjustments for optimal mushroom growth.
The second box, the laminar flow hood, is dedicated to the sterilization of fruiting bags and spawn. Unlike the growing chamber, it operates independently and is not connected to the IoT or AI system.
To complete the ecosystem, MASH also includes an e-commerce platform that supports transactions exclusively for white oyster mushrooms—both raw and processed. The platform connects mushroom growers using the MASH system with potential buyers, streamlining the supply chain and encouraging sustainable local production and trade.

Project Objectives
General Objective:  
To be able to integrate an IoT and AI system for automated growing of white oyster mushrooms (Pleurotus florida), supported by an e-commerce platform, that increases yield by 10-20%, reduces contamination incidents by 85%, optimizes resource use, and facilitates direct, sustainable market access for small-scale farmers in the Philippines.
Specific Objectives: 


To receive user inputs from both growers and consumers through the e-commerce platform, such as product listings, order placements, and payment data.
To capture key environmental data—specifically temperature, humidity, and CO₂ levels—in real-time from within a mushroom growing chamber via an IoT device.
To sterilize the mushroom fruiting bags using a modified big fan equipped with a HEPA filter to minimize contamination risks before placement inside the growing chamber.
To load  the sterilized fruiting bags for optimized placement within the chamber to ensure uniform exposure to environmental controls.
To regulate airflow and automate environmental controls through actuators based on integrated AI analysis, thereby maintaining the prescribed environment.
To calculate proper growing state for white oyster mushroom using integrated AI model
To manage product listings, inventory, orders, and payments via an integrated e-commerce platform connecting growers and consumers.
To provide real-time environmental data and system alerts through both an integrated LCD module and a mobile application for direct and remote monitoring


Scope
This study focuses on the development and implementation of a smart oyster mushroom (Pleurotus florida) cultivation system through indoor farming, integrating IoT-based environmental monitoring and control technologies. The project encompasses the following key aspects:
Indoor Mushroom Cultivation: Controlled environment cultivation within a sealed, well-regulated growth chamber designed to minimize pest infiltration and contamination, maintaining optimal conditions for consistent mushroom growth.
IoT Environmental Monitoring: Deployment of sensors for monitoring temperature, humidity, and carbon dioxide levels in real time, linked to automated actuators for environmental regulation.
Mobile Application for Growers: A dedicated mobile application will be developed for growers. It includes a dashboard for real-time monitoring of the grow chamber, remote control of the IoT system's actuators, and a log for cultivation activities.
E-commerce Platform Integration: Development of a comprehensive multi-platform e-commerce system (mobile and web), designed to connect growers, middlemen, and consumers. This platform supports direct sales, product listing, order processing, payment gateways, and logistics coordination to expand market reach and improve profitability.
Real-Time and Offline Database Synchronization: Environmental and sales data will be synchronized live across devices using Firebase Realtime Database, ensuring timely decision-making and efficient farm management. Recognizing possible internet outages in remote rural locations, the system is designed to operate offline using SQLite for local data storage during disconnects. Once connectivity is restored, the local data will synchronize seamlessly with the cloud, ensuring no data loss or disruption in monitoring and operations.



Limitation
Despite the comprehensive scope, the project is subject to the following limitations:
Species Focus: The system is tailored specifically for the cultivation of white oyster mushrooms (Pleurotus florida). Adaptation to other mushroom species, which may have different environmental requirements, is outside the current study.
Scale: The current design and implementation focus on an indoor farming scale suitable for small growers only. Large-scale commercial operations or open-field cultivation settings are not within the scope of this phase .
Technology Accessibility: The system assumes availability of stable internet access for real-time data transmission and e-commerce platform usage, which may be constrained in remote areas without reliable connectivity.
Resource Constraints: Affordability, maintenance of IoT devices, and the need for continuous Alternating Current power supply may pose challenges for some smallholder farmers, which are not covered within this study's implementation plan.

Detailed Functionalities including the users 
The M.A.S.H. system is designed as a modular solution combining hardware automation, IoT-enabled monitoring, AI-driven optimization, and e-commerce to holistically address challenges throughout the oyster mushroom cultivation cycle. It is structured into three development phases, each progressively enhancing system capabilities and market integration.
Method Phase 1: Foundation — Basic Monitoring and Automation
This phase establishes the digital backbone of mushroom growing, introducing continuous environmental monitoring and automated regulation. The system deploys a network of IoT sensors (temperature, humidity, CO₂) interfaced with automated actuators such as humidifiers and airflow fans equipped with HEPA filtration to maintain an optimal and sterile growing environment . This real-time data is relayed to mobile and web applications enabling growers to remotely monitor and intervene as needed, significantly reducing human error and resource waste.
User Roles:
Owner/Admin: Has full system oversight, manages site creation, user roles, and accesses detailed analytics to gauge overall farm performance.
Grower: Monitors growth conditions, receives AI-generated alerts, adjusts environmental parameters where allowed, and logs cultivation activities through the Grower Mobile Application ..


Method Phase 2: Enhancement — Contamination Control and Market Integration
Building on Phase 1, Phase 2 integrates advanced contamination prevention and detection strategies. IoT-controlled sterilization units and automated HEPA filters to help maintain hygienic grow rooms, significantly reducing contamination risks, which are major challenges in oyster mushroom production . AI algorithms analyze environmental data patterns and alert growers to early signs of contamination, enabling timely response and minimized crop losses.
Concurrently, an e-commerce portal is introduced, accessible via both mobile and web applications, where growers can register, upload product listings , and manage orders. The platform supports digital payments and logistics coordination, linking producers directly to consumers, retailers, and restaurants, enhancing market access and income stability .
User Roles:
Grower: Utilizes mobile e-commerce app to market fresh or processed mushrooms, monitor sales, and manage inventory. Can also monitor contamination status and receive optimization recommendations.
Buyer: Accesses e-commerce marketplace to purchase products, track orders, and provide feedback.
System Administrator: Manages platform maintenance, user accounts, product approvals, and oversees system-wide contamination and market analytics.


Method Phase 3: Optimization — Continuous Harvest Cycle Management and Yield Maximization
The final phase emphasizes productivity extension of harvested fruiting bags of Pleurotus florida. IoT sensors continuously track microclimate variables (humidity, CO₂, temperature) inside grow facilities, while AI-assisted algorithms alert growers to environmental shifts that may stress fruiting bags or reduce yield . Automated misting and ventilation are adjusted dynamically to maintain optimal growth conditions and maximize flush cycles.
Data from this phase feeds back into performance dashboards accessible by all relevant users, facilitating informed management decisions, yield forecasting, and sustainability assessment.
Software Applications Overview
Grower Mobile Application:
Real-time monitoring, AI alerts and environmental control interface, 
Mobile E-Commerce Application:
Consumer-facing interface for browsing mushroom products, making purchases, order tracking, and payment processing.
Web Dashboard for System Administrators:
Comprehensive registered chamber and platform management tools with analytics on sales and the active or inactive status of each registered unit or chamber
Public Website and E-Commerce Platform:
Facilitates product listing, direct sales, and logistics for growers, and consumers.

Budget 
Item
Cost
Shop Link
Raspberry Pi Zero 2W
₱1,600.00
https://www.makerlab-electronics.com/products/raspberry-pi-zero-2w-sc1146?_pos=1&_sid=d7d2567e7&_ss=r?variant=43985610145983 
Micro USB Power Switch
₱70.00
https://shopee.ph/ITHT-USB-Type-C-With-ON-OFF-Switch-Power-Button-30CM-Charging-Extension-Cable-Universal-Type-C-Extension-Cable-new-i.168902097.43350919209?sp_atk=b044206a-8b9b-4dd5-a3d8-03e90e5c3284&xptdk=b044206a-8b9b-4dd5-a3d8-03e90e5c3284
CO2L Unit with Temperature and Humidity Sensor
₱3,090.00
https://www.makerlab-electronics.com/products/m5stack-co2l-unit-with-temperature-and-humidity-sensor-scd41?_pos=2&_sid=e47226585&_ss=r?variant=43081515696319 
I2C 20x4 Arduino LCD Display Module
₱280.00
https://www.makerlab-electronics.com/products/20x4-lcd-display-i2c-white-blue?_pos=2&_psq=20x4&_ss=e&_v=1.0 
Breadboard Jumper Wires
₱50.00
https://www.makerlab-electronics.com/products/40-pin-10cm-jumper-wires?_pos=1&_psq=jum&_ss=e&_v=1. 
Mini Fan (exhaust)
₱75.00
https://www.makerlab-electronics.com/products/raspberry-pi-fan?_pos=1&_sid=749a1aca7&_ss=r?variant=42698395844799 
Humidifier
₱135.00
https://shopee.ph/DC5V-Unswitched-Four-Spray-Humidifier-Module-Atomization-Control-Board-i.1118156654.41163184713?sp_atk=3edd6c00-9de8-4982-9c17-dcb67524fa2d&xptdk=3edd6c00-9de8-4982-9c17-dcb67524fa2d
Hepa Filter
₱400.00
https://shopee.ph/Sharp-FZ-F30HFE-Air-Purifier-Composite-Filter-For-FP-F30-FP-GM30E-KC-F30E-FP-J30E-FP-JM30-FP-GM30B-B-i.1242063782.41350010111?sp_atk=7461583e-d700-4f38-9eb-357085a0a0b8&xptdk=7461583e-d700-4f38-9eb-357085a0a0b8
Blower Fan (12 inch) (Air intake)
₱1,000.00
https://shopee.ph/Exhaust-fan-Low-Noise-Kitchen-Exhaust-Fan-Wall-Mounted-Home-Exhaust-Fan-Multi-size-Ventilation-Fan-i.629450377.26465497321?sp_atk=4e16bf8f-a46a-4319-95c4-b47e45fcc5c3&xptdk=4e16bf8f-a46a-4319-95c4-b47e45fcc5c3
Air Filtered Fan (4 inch)
₱2,300.00
https://shopee.ph/%E3%80%90Remote-Control%E3%80%91-Xiaomi-DIY-Air-Purifier-Set-Exhaust-Fan-Extractor-Fan-with-for-Version2-2S-2H-2C-3H-i.955280135.29637047541 
Grow Tent (24 x 24 x 36 inch)
₱4,789.00
https://shopee.ph/%E3%80%90Litgrow%E3%80%91Garden-80-x-80-x-160-CM(32-x32-x64-)-Hydroponic-Indoor-Bud-Green-Room-600D-Grow-Tent-i.980116806.16894088199?sp_atk=1980a628-6da2-4df3-a067-4e2cbe8b5323&xptdk=1980a628-6da2-4df3-a067-4e2cbe8b5323 
Fan Speed Control Board 
₱200.00
https://oshpark.com/shared_projects/oJIFTsvc 
Panel Mount Audio Jack
₱90.00
https://shopee.ph/1-3-5PCS-3.5MM-Audio-Jack-Socket-Stereo-3-Pole-Solder-Panel-Mount-With-Nut-Connector-Headphone-Female-Socket-PJ-392A-PJ392A-i.1263679380.28166723113?sp_atk=96e96bde-90b2-4a78-a5fd-1e501b0f911f&xptdk=96e96bde-90b2-4a78-a5fd-1e501b0f911f
Power strip smart socket
₱1,799.00
https://shopee.ph/LASCO-Wifi-Universal-Smart-Power-Strip-with-Energy-Monitoring-Smart-Socket-with-Surge-Pro-i.151900297.23955304247?sp_atk=de59679c-ffba-45a3-afe3-7ba7a2705502&xptdk=de59679c-ffba-45a3-afe3-7ba7a2705502
F5305S Power Mosfet Module
₱150.00
https://www.makerlab-electronics.com/products/f5305s-power-mosfet-module?_pos=1&_sid=89c1bf8df&_ss=r?variant=42290995298495
TOTAL
₱16,028.00



Model of the device/s included in the proposed project / Prototype Figma
The M.A.S.H. system integrates both advanced hardware devices and multi-platform software applications designed to create an optimized, automated, and sustainable mushroom cultivation ecosystem.
FIGMA Design:  M.A.S.H. Design Figma  


Diagrams:  User Flow Diagram
Hardware Components
Compact Mushroom Growing Chamber:
A sealed, climate-controlled chamber embedded with multiple environmental IoT sensors monitoring temperature, humidity, and carbon dioxide. This chamber maintains the regulated mushroom cultivation environment essential for consistent and high-quality Pleurotus florida growth. Precision control is achieved using actuators such as humidifiers, fans with HEPA filtration to provide sterile airflow similar to a Laminar Flow Hood, which reduces contamination risks during critical growth phases .


Software Applications and Interfaces
The project features four interrelated digital platforms tailored to engage different user types and streamline operations from cultivation to sales:
Mobile Application (Grower App):
 Designed for mushroom cultivators, this application provides real-time access to environmental data, AI-driven alerts (e.g., contamination detection), and remote control over grow chamber parameters. It supports logging cultivation metrics, viewing growth progress, and receiving maintenance reminders .
Mobile Application (E-commerce for Consumers):
 A consumer-facing app facilitating mushroom product browsing, purchasing, and order tracking. It supports payment processing and provides product information with traceability, increasing buyer confidence and enabling direct sales from growers to end consumers.
Web Dashboard (System Administrators):
 An administrative portal for managing the entire ecosystem including multiple grow sites, user roles, IoT devices, and energy systems. The dashboard offers comprehensive analytics, farm status monitoring, and system configuration controls, designed for technical support and operational oversight .
Website E-commerce Platform:
 A public-facing website that connects growers, middlemen, and consumers. It features product catalogs, order management, digital payment gateways, and logistics coordination tools to enhance market access and business scalability.


Prototype Visualization with Figma
All user interface (UI) and user experience (UX) designs for the mobile and web applications were developed as interactive wireframes using Figma. These prototypes clearly demonstrate intuitive navigation flows, real-time monitoring dashboards, alert systems, and e-commerce shopping experiences. The design approach prioritizes user-friendliness, accessibility across devices, and seamless integration with backend IoT and AI systems, providing a comprehensive preview of the system's functionality and look.

Provide an IPO diagram (Input – Process – Output) 
Input
Process
Output
Real-time sensor data including temperature (±0.5°C), humidity (±2%), CO₂ levels, and sterilization status; battery charge; user sales and order data from e-commerce platform
AI and machine learning algorithms analyze sensor inputs to optimize environmental parameters dynamically. E-commerce module processes sales orders, manages inventory, and coordinates logistics via integrated backend
Automated environmental control adjustments (actuator commands for humidifiers, fans, sterilizers), contamination alerts issued to users, real-time performance dashboards, user notifications, order tracking updates, and sales analytics reports



REASON(s) / JUSTIFICATION(s) IN CHOOSING THE PROJECT:
Global and local food insecurity continues to worsen due to population growth, climate change, and resource constraints, necessitating sustainable and nutritious food alternatives . Mushrooms, particularly Pleurotus species, offer an effective solution to this challenge because they mature rapidly, thrive in small spaces, and provide a rich source of highly bioavailable protein, essential vitamins, minerals, and antioxidants, while maintaining a low environmental footprint .
Unlike conventional livestock, mushroom cultivation requires minimal land and water and generates significantly fewer greenhouse gas emissions, positioning it as an environmentally responsible nutrient source (. In urban and rural contexts, mushrooms can be farmed efficiently with limited inputs, thereby supporting food production in areas with constrained agricultural space and resources .
Traditional methods of mushroom farming, however, are often manual, laborious, and prone to contamination, leading to losses and waste. Integrating Internet of Things (IoT) and Artificial Intelligence (AI) technologies provides precision environmental control that avoids contamination, optimizes growth parameters, and reduces resource use by automating monitoring and adjustments . This smart farming approach enhances yield quality, encourages sustainable practices, and increases labor efficiency.
Additionally, e-commerce platforms simplify product distribution, overcoming barriers posed by intermediaries and limited market access commonly faced by smallholder farmers. This digital marketplace facilitates direct sales, fairer pricing, and improved income stability for producers .
Together, these technologies enable a comprehensive, sustainable, and economically viable model for oyster mushroom farming that addresses urgent food security, environmental sustainability, and rural livelihood challenges in the Philippines. The M.A.S.H. project aligns with the Philippine Development Plan's goals to improve food security and promote agricultural modernization (Philippine Development Plan, 2023), while also contributing to the United Nations Sustainable Development Goals such as Zero Hunger (SDG 2), Clean Energy (SDG 7), and Decent Work and Economic Growth (SDG 8).

1. Summary of Interview with Mr. Cristobal R. Carcelia Jr. (Small-Scale Grower)
Date: August 9 & 12, 2025 Location: Caloocan City Perspective: Urban, Small-Scale Cultivator
The interviews with Mr. Carcelia, an experienced oyster mushroom grower, confirmed the daily challenges faced by urban cultivators and validated the core premise of the M.A.S.H. system.
Key Problems Validated:
Environmental Control is Critical: Mr. Carcelia emphasized that maintaining a cool, dark, and humid environment is paramount. The hot Philippine climate, especially during summer, is a significant obstacle to consistent production, validating the need for an IoT system to automate temperature and humidity control.
Contamination and Pests are Major Risks: He cited insect infestation as the single biggest problem. He also noted that contamination can originate from low-quality fruiting bags, which must be removed immediately to prevent widespread loss. This highlights the necessity of the proposed contamination detection and prevention features.
Inconsistent Fruiting Bag Quality: The success of a harvest is highly dependent on the quality of purchased fruiting bags, a factor he described as "luck-based" (swertihan), which justifies the project's goal of maximizing the yield and lifespan of every bag.
Support for the M.A.S.H. Solution:
High Receptiveness to Technology: When presented with the concept of a mobile app for monitoring the grow environment, Mr. Carcelia responded with "Ay, of course. Yeah. Yeah."). He immediately recognized the value of real-time sensor data.
Willingness to Invest: He confirmed he would be willing to invest in the proposed IoT device, viewing the estimated prototype cost as reasonable for a small-scale setup.
Justification for E-Commerce: Mr. Carcelia detailed the significant price disparity between the low "gate price" paid by wholesalers and the higher retail price. He affirmed that selling directly to consumers is the "best" way to maximize income, directly supporting the inclusion of an e-commerce platform.
2. Summary of Interview with Mr. Ramel (Fruiting Bag Producer, Mushroom Goods Producer and Mushroom Grower)
Date: August 10, 2025 Perspective: Commercial Producer
The interview with Mr. Ramel, whose business focuses on producing and selling fruiting bags, provided critical insights from an upstream, supply-side perspective.
Key Problems and Processes Validated:
Contamination is the Primary Production Hurdle: From his perspective, contamination originates from the initial spawn (binhi), insufficient pasteurization, or pests. This validates the project's intense focus on contamination reduction as a core feature.
Reliance on Manual Monitoring: Mr. Ramel gauges the environment's condition based on his own physical sensation ("pakiramdam ko") rather than precise sensors, indicating a clear opportunity for a data-driven, automated system to improve consistency.
Weather Dependency: He confirmed that summer is the most challenging period, requiring manual intervention to prevent fruiting bags from drying out, which supports the need for a climate-controlled chamber.
Support for the M.A.S.H. Solution:
Validation of IoT Chamber Design: Upon reviewing the design for the automated growing chamber, Mr. Ramel affirmed its technical correctness ("Okay yung lahat ng ano, sakto lahat dun... tama naman yung ginagawa niya").)
Justification for Lifespan Extension Goal: He agreed that the primary reason bags stop producing is that they dry out. He validated that the system's humidifier would directly address this issue and prolong the harvest.
Market Opportunity: His business model, which involves selling fruiting bags to aspiring growers, reveals a secondary market for the M.A.S.H. system as a valuable add-on for his customers.

3. Summary of Consultation with Ms. Hazel (BPI Mushroom Expert)
Date: August 20, 2025 Location: Bureau of Plant Industry, Manila Perspective: Scientific and Industry Expert
The consultation with a mushroom specialist from the Bureau of Plant Industry provided critical, strategic guidance to refine the project's scope and ensure its academic and practical feasibility.
Key Strategic Recommendations:
Drastically Narrow the Project Scope: The expert's most critical advice was to focus exclusively on the post-harvesting stage and a single variety (white oyster mushroom) to ensure the project is achievable within the thesis timeline.
Target Medium to Large-Scale Growers: The proposed high-tech system is best suited for established enterprises with the capacity to invest in and maintain it.
Refine Project Framing: The title should be academic, using phrases like "Development of...", and the rationale should be structured to first present the problem (challenges in mushroom farming) and then the solution (the M.A.S.H. system).
Actionable Guidance for the Proposal:
Define a Concrete Yield Goal: The project should aim to increase the typical yield of 800 grams per bag by a specific, measurable target (e.g., 20%).
Incorporate Specific Technical Parameters: The IoT sensors must be calibrated to precise scientific standards for white oyster mushrooms (e.g., Temp: 25-28°C, Humidity: 80-90%, CO₂: 10k-15k ppm).
Ensure Feasibility with On-Site Visits: The expert stressed the importance of visiting at least two farms to gather real-world data and ensure the project is realistic, not just theoretical. She also recommended collaborating with the DTI to verify the business case and ROI.


Feasibility Study
This study assesses the viability of the M.A.S.H. project across three critical domains: operational, technical, and economical feasibility. The analysis integrates findings from stakeholder interviews with a small-scale grower (Mr. Cristobal R. Carcelia Jr.), a commercial producer (Mr. Ramel), and a scientific expert from the Bureau of Plant Industry (Ms. Hazel), confirming the project's practicality and potential for impact.
1. Operational Feasibility
The operational feasibility of the M.A.S.H. system is high, as it directly addresses the day-to-day challenges faced by local mushroom growers and aligns with their expressed needs and workflows.
Deployment & User Acceptance: The interviews confirmed a strong enthusiasm for the proposed technology. Mr. Carcelia, representing the target end-user, responded with "Ay, of course. Yeah.." when presented with the concept of a mobile monitoring app. This indicates a high level of user acceptance and a low barrier to deployment for willing growers. The system is designed for a small-scale, indoor setup which is common for urban and semi-urban cultivators.
User Workflow: The proposed system significantly improves upon the current user workflow. Mr. Ramel currently relies on physical sensation ("pakiramdam ko") to gauge environmental conditions, a method prone to inconsistency. The M.A.S.H. system replaces this subjective process with a data-driven workflow, allowing for precise monitoring and control via a mobile app. This aligns with modern agricultural practices and reduces the potential for human error.
Maintenance: The hardware components are based on readily available off-the-shelf parts (Raspberry Pi, sensors, fans). Maintenance will primarily involve standard upkeep such as refilling the humidifier, cleaning the grow tent, and periodic checks of the electronic components, which is well within the capacity of the target users. The system automates the most labor-intensive part of the process: constant environmental monitoring.
Resource Needs: The system requires a stable power source and internet connectivity for real-time features, which are noted as limitations in remote areas. However, for the target urban and semi-urban growers in places like Caloocan, these resources are generally available. The inclusion of offline data storage with SQLite for later synchronization is a practical solution that mitigates the impact of intermittent connectivity.
2. Technical Feasibility
The project is technically sound, utilizing a well-defined, modern technology stack and proven hardware components that have been validated by industry practitioners.
Hardware Choices & Integration: The selection of a Raspberry Pi Zero 2W as the controller, coupled with specific sensors for temperature, humidity, and CO₂, is a standard and effective approach for IoT projects. The components are accessible and have extensive documentation.
Software Stack: The proposed stack—Flutter for the cross-platform mobile app, NestJS/Next.js for the web backend, and PostgreSQL/Firebase for the database—is a scalable, and modern choice. This stack allows for rapid development, a rich user experience, and efficient data management.
Risk Mitigation: The team has identified key technical risks and proposed viable mitigation strategies.
Contamination: This is the primary risk cited by both Mr. Carcelia and Mr. Ramel. The system directly addresses this through a controlled environment with HEPA-filtered airflow. The AI component's goal of early contamination detection further reduces this risk.
Connectivity: As mentioned, the use of SQLite for offline functionality ensures the system remains operational during internet outages, a critical feature for agricultural technology in the Philippines.


3. Economical Feasibility
The project is economically viable for both the development phase and for potential end-users, demonstrating a clear path to a positive return on investment.
Cost Breakdown: The detailed budget in the proposal lists the total hardware cost as ₱16,028.00. This is well within the team's working budget of ₱20,000, leaving ample room for contingencies, software subscriptions, and other project-related expenses. The cost is manageable and demonstrates responsible financial planning.
Cost-Benefit & Return on Investment (ROI): The economic benefits for a grower adopting the M.A.S.H. system are significant:
Increased Yield & Reduced Losses: The system directly combats the main causes of crop failure—environmental instability and contamination—which, according to stakeholders, are major issues, especially in the Philippine climate. Following the BPI expert's advice, a target yield increase of 20% is a measurable and achievable goal that would directly boost revenue.
Higher Profit Margins: Mr. Carcelia confirmed the large price disparity between the low "gate price" from wholesalers and the higher retail price. He stated that selling directly to consumers is the "best" way to maximize income. The integrated e-commerce platform facilitates this, bypassing middlemen and allowing growers to capture more of the final sale price.
Willingness to Invest: The most compelling evidence for the system's economic feasibility is Mr. Carcelia's confirmation that he would be willing to invest in the proposed device, viewing the prototype cost as reasonable for a small-scale operation. This serves as direct market validation for the product's value proposition.
Sustainability of Funding: For the scope of the thesis, the project is fully funded by the team's budget. Beyond academia, the system's demonstrated ability to increase profitability for growers creates a sustainable business model where the initial investment in the M.A.S.H. device is recovered through improved sales and yields.

Give at least (5) evidences that your proposed project is workable (feasible)
IoT-Based Environmental Monitoring and Control Improves Yield
Chanda, Akter, and Sarker (2023) developed an IoT-based environmental monitoring and control system for home-based mushroom cultivation. Their system continuously measures temperature, humidity, and CO₂, automatically regulating actuators to maintain optimal conditions. Results showed improved yield consistency and reduced labor errors, confirming that IoT-enabled automation significantly enhances mushroom farming productivity. The system's remote monitoring capability also allows timely interventions, reducing contamination and spoilage risks.
Source:
Chanda, R., Akter, S., & Sarker, S. (2023). Internet of Things (IoT)-based environmental monitoring and control system for home-based mushroom cultivation. Sensors, 23(2), 9856179. https://pmc.ncbi.nlm.nih.gov/articles/PMC9856179/
AI and Image Processing Elevate Smart Mushroom Farming Performance
Raghavan (2024) demonstrated the use of AI-driven image processing and IoT sensors in enhancing oyster mushroom cultivation. The AI optimizes environmental parameters and detects diseases early through computer vision, leading to higher yields and better product quality. The integration of these technologies in a mobile/web-based platform improved decision-making efficiency for growers, confirming the feasibility of intelligent systems for small-to-medium scale mushroom farms.
Source:
Raghavan, P. (2024). Smart mushroom farming: Integrating IoT and image processing for enhanced cultivation [Bachelor’s thesis, Metropolia University of Applied Sciences]. Theseus. https://www.theseus.fi/bitstream/handle/10024/872115/Raghavan_Parthsarthi.pdf?sequence=2
Intelligent Monitoring Systems Increase Efficiency in Oyster Mushroom Cultivation
Prasetyo and Susanto (2022) developed an IoT-based intelligent monitoring system for grey oyster mushrooms, integrating sensors and AI to continuously assess cultivations. They reported that their system reduced the need for manual checks, minimized contamination, and improved environmental stability, resulting in better crop uniformity and productivity. Their findings affirm the practical benefits of IoT and AI integration in mushroom cultivation systems like M.A.S.H.
Source:
Prasetyo, Y., & Susanto, R. (2022). Intelligent monitoring of grey oyster mushroom cultivation with IoT. International Journal of Intelligent Systems and Applications in Engineering, 10(3), 3787. https://www.ijisae.org/index.php/IJISAE/article/view/3787
Local and Governmental Support for Mushroom Farming Feasibility
The Philippine Department of Agriculture (DA) has acknowledged mushroom cultivation as a lucrative and sustainable livelihood intervention, providing strategic support programs and funding for smallholder farmer technology adoption (Department of Agriculture, 2024). Local feasibility studies, such as those by Gungob and Magadan (2024), highlight that modernized mushroom production—including environmental control systems—can increase yields by up to 30% and stabilize farmer incomes significantly, substantiating the local applicability and economic viability of the M.A.S.H. system.
Sources:
Department of Agriculture Philippines. (2024). Philippine mushroom development program: Strategic roadmap 2024-2030.
Gungob, C., & Magadan, H. (2024). The economics of production and marketing of oyster mushrooms (Pleurotus ostreatus) in Bukidnon, Philippines. Asian Journal of Agricultural Extension, Economics & Sociology, 42(11), 186–196. https://doi.org/10.9734/ajaees/2024/v42i112604



Modernized Mushroom Production Enhances Profitability for Farmers
Gungob and Magadan (2024) highlighted that modernized mushroom production systems, particularly those using environmental control technologies, can increase yields by up to 30% and significantly stabilize farmer incomes. Their study of oyster mushroom economics in Bukidnon, Philippines, affirms that adopting smart farming systems is not only technically viable but also economically rewarding for local growers.
Source: 
Gungob, C., & Magadan, H. (2024). The economics of production and marketing of oyster mushrooms (Pleurotus ostreatus) in Bukidnon, Philippines. Asian Journal of Agricultural Extension, Economics & Sociology, 42(11), 186–196. https://doi.org/10.9734/ajaees/2024/v42i112604



EXPECTED CONTRIBUTIONS TO THE GROWTH OF KNOWLEDGE IN INFORMATION TECHNOLOGY:
This project is poised to make several significant contributions to the advancement of information technology, particularly within the realm of smart agriculture and precision farming:
Integration of AI and IoT in Oyster Mushroom Cultivation:
The project proposes a novel combination of Artificial Intelligence (AI), and Internet of Things (IoT) devices to automate and optimize white oyster mushroom (Pleurotus florida) cultivation, including environmental monitoring, contamination control, and energy management. This integration advances existing agricultural technology frameworks by addressing sustainability and operational autonomy, especially in off-grid rural farming contexts .
E-commerce Platform Integration for Agricultural Business Growth:
By embedding e-commerce functionalities directly linked to cultivation and harvest data, this project introduces an innovative model of farm-to-market digital transformation. It facilitates direct connection of growers to consumers and retailers, improving market efficiency, income stability, and adoption of digital commerce in rural agriculture sectors . This contribution bridges agricultural technology with supply chain management systems.
Scalable Model Applicable to Diverse Indoor Farming Systems:
The modular design combining IoT environmental control, AI decision-making, and digital sales platforms can be adapted to other indoor crop systems beyond oyster mushrooms. This opens pathways for replication and scaling in urban farming, vertical farms, and other controlled environment agriculture solutions .
Advancement in Smart Farming and Digital Agriculture Knowledge:
The research contributes empirical data and tested methodologies on deploying AI-enhanced IoT systems with renewable energy in precision mushroom farming. It adds to scientific literature on sensor design, machine learning for contamination detection, energy-aware farming systems, and human-computer interfaces in agriculture, stimulating further academic inquiries and technological applications . 

Data-Driven Crop Management and Yield Optimization:
Utilization of real-time sensor data coupled with AI algorithms for continuous environmental adjustment and contamination prevention improves yield reliability and sustainability. This level of digital agriculture intelligence supports decision-making processes enhancing productivity while minimizing resource wastage, exemplifying practical applications of Industry 4.0 in agritech . 



Proposed by: 	
Llanes, Kevin A.
0956-9552-808
Project Manager
Antang, Irheil Mae S. 
0929-8986-408 
Software Engineer
Bae, Ma, Catherine H. 
0907-3796-586
Front-end Developer
Failana, Jin Harold A. 
0910-3633-455
Hardware Programmer
Namias, Jhon Keneth Ryan B.
0927-2533-969
Back-end Developer
Pabua, Emmanuel L. 
0993-503-4689
Database Administrator
Valencia, Ronan Renz T.
0985-845-9039
Full Stack Developer




Approved by:
Prof. Joemen G. Barrios, MIT
Thesis Adviser




References:
Abdelkader, H. A., & Elshafie, M. A. (2023). A new solar-IoT based method for mushroom cultivation. Journal of Electrical Systems, 19 (4), 4821–4832. https://journal.esrgroups.org/jes/article/download/6990/4821/12854
Amara, I. B., & El-Baky, H. H. A. (2023). Environmental benefits of edible mushroom farming. Sustainable Agriculture Reviews.
Zeng, X., Li, J., Lyu, X., Chen, T., Chen, J., Chen, X., & Guo, S. (2023). Utilization of functional agro-waste residues for oyster mushroom production: Nutritions and active ingredients in healthcare. Frontiers in Plant Science, 13. https://doi.org/10.3389/fpls.2022.1085022 
Rodriguez, J. M. (2024). Unveiling the mushroom Value Chain: Opportunities and constraints in Partido District, Camarines Sur, Philippines. Jurnal Manajemen Dan Agribisnis. https://doi.org/10.17358/jma.21.1.13
Aditya, N., Neeraj, N., Jarial, R., Jarial, K., & Bhatia, J. (2024). Comprehensive review on oyster mushroom species (Agaricomycetes): Morphology, nutrition, cultivation and future aspects. Heliyon, 10(5), e26539. 
https://doi.org/10.1016/j.heliyon.2024.e26539
Domingo, A. (2025). Mushroom production in Nueva Ecija: Promoting entrepreneurship and driving SDG achievement for sustainable development. Journal of Lifestyle and SDGs Review, 5(3), e04172. https://doi.org/10.47172/2965-730x.sdgsreview.v5.n03.pe04172
Quion, K., Lastomen, M. G., Lavapıes, J., Sebugon, J., & Baguın, R. (2023, December 26). Assessment of mushroom (Pleurotus ostreatus) production in Bohol, Philippines. https://dergipark.org.tr/en/pub/ejar/issue/81751/1410456
Gungob, C., & Magadan, H. (2024). The Economics of Production and Marketing of Oyster Mushrooms (Pleurotus ostreatus) in Bukidnon, Philippines. Asian Journal of Agricultural Extension, Economics & Sociology, 42(11), 186–196. https://doi.org/10.9734/ajaees/2024/v42i112604
Pipaliya, G., & Ansari, M. A. (2023). Exploring the challenges and constraints encountered by mushroom growers in Uttarakhand: a comprehensive study. Asian Journal of Agricultural Extension Economics & Sociology, 41(12), 1–8. https://doi.org/10.9734/ajaees/2023/v41i122297
Aniama, S. O. (2023). Challenges of global food insecurity. African Journal of Sustainable Development, 12(1), 45–58.
Buzdar, M. A., et al. (2020). Influence of environmental conditions on mushroom cultivation: A review. Mycology, 10(3), 150-161.
Chanda, R., Akter, S., & Sarker, S. (2023). Internet of Things (IoT)-based environmental monitoring and control system for home-based mushroom cultivation. Sensors, 23(2), 9856179. https://pmc.ncbi.nlm.nih.gov/articles/PMC9856179/
Department of Agriculture Philippines. (2024). Philippine mushroom development program: Strategic roadmap 2024-2030.
Ekun, B. A., et al. (2021). Edible mushroom farming: Dietary and ecological benefits. Ecological Agriculture Journal, 15(2), 112-126.
Gungob, C., & Magadan, H. (2024). The economics of production and marketing of oyster mushrooms (Pleurotus ostreatus) in Bukidnon, Philippines. Asian Journal of Agricultural Extension, Economics & Sociology, 42(11), 186–196. https://doi.org/10.9734/ajaees/2024/v42i112604
Huidrom, S. D., et al. (2024). Design and implementation of an IoT-based microclimate control system for oyster mushroom cultivation. International Journal of Agricultural Technology, 20(4), 1315–1324.
Kumar, R., Patel, S., & Singh, A. (2024). IoT-enabled precision agriculture: Impact on crop quality and farmer profitability. Smart Agriculture Technology, 8(3), 156–171.
Prasetyo, Y., & Susanto, R. (2022). Intelligent monitoring of grey oyster mushroom cultivation with IoT. International Journal of Intelligent Systems and Applications in Engineering, 10(3), 3787. https://www.ijisae.org/index.php/IJISAE/article/view/3787
Raghavan, P. (2024). Smart mushroom farming: Integrating IoT and image processing for enhanced cultivation [Bachelor’s thesis, Metropolia University of Applied Sciences]. Theseus. https://www.theseus.fi/bitstream/handle/10024/872115/Raghavan_Parthsarthi.pdf?sequence=2
A global food crisis | World Food Programme. (n.d.). UN World Food Programme (WFP). https://www.wfp.org/global-hunger-crisis
sustainE. (2025, March 14). Edible mushroom farming: a viable protein alternative and the need for public education in southwest Nigeria. SustainE. https://sustaine.org/edible-mushroom-farming-a-viable-protein-alternative-and-the-need-for-public-education-in-southwest-nigeria/
Zhang, L., Wang, H., & Chen, M. (2024). Smart agriculture using IoT and machine learning for precision farming. Computers and Electronics in Agriculture, 198, 107045.