# M.A.S.H. Project Feasibility Study

## Overview
This study assesses the viability of the M.A.S.H. project across three critical domains: operational, technical, and economical feasibility. The analysis integrates findings from stakeholder interviews with a small-scale grower (Mr. Cristobal R. Carcelia Jr.), a commercial producer (Mr. Ramel), and a scientific expert from the Bureau of Plant Industry (Ms. Hazel), confirming the project's practicality and potential for impact.

## 1. Operational Feasibility
The operational feasibility of the M.A.S.H. system is high, as it directly addresses the day-to-day challenges faced by local mushroom growers and aligns with their expressed needs and workflows.

### Deployment & User Acceptance
The interviews confirmed a strong enthusiasm for the proposed technology. Mr. Carcelia, representing the target end-user, responded with "Ay, of course. Yeah.." when presented with the concept of a mobile monitoring app. This indicates a high level of user acceptance and a low barrier to deployment for willing growers. The system is designed for a small-scale, indoor setup which is common for urban and semi-urban cultivators.

### User Workflow
The proposed system significantly improves upon the current user workflow. Mr. Ramel currently relies on physical sensation ("pakiramdam ko") to gauge environmental conditions, a method prone to inconsistency. The M.A.S.H. system replaces this subjective process with a data-driven workflow, allowing for precise monitoring and control via a mobile app. This aligns with modern agricultural practices and reduces the potential for human error.

### Maintenance
The hardware components are based on readily available off-the-shelf parts (Raspberry Pi, sensors, fans). Maintenance will primarily involve standard upkeep such as refilling the humidifier, cleaning the grow tent, and periodic checks of the electronic components, which is well within the capacity of the target users. The system automates the most labor-intensive part of the process: constant environmental monitoring.

### Resource Needs
The system requires a stable power source and internet connectivity for real-time features, which are noted as limitations in remote areas. However, for the target urban and semi-urban growers in places like Caloocan, these resources are generally available. The inclusion of offline data storage with SQLite for later synchronization is a practical solution that mitigates the impact of intermittent connectivity.

## 2. Technical Feasibility
The project is technically sound, utilizing a well-defined, modern technology stack and proven hardware components that have been validated by industry practitioners.

### Hardware Choices & Integration
The selection of a Raspberry Pi Zero 2W as the controller, coupled with specific sensors for temperature, humidity, and CO₂, is a standard and effective approach for IoT projects. The components are accessible and have extensive documentation.

### Software Stack
The proposed stack—Flutter for the cross-platform mobile app, NestJS/Next.js for the web backend, and PostgreSQL/Firebase for the database—is a scalable, and modern choice. This stack allows for rapid development, a rich user experience, and efficient data management.

### Risk Mitigation
The team has identified key technical risks and proposed viable mitigation strategies.

#### Contamination
This is the primary risk cited by both Mr. Carcelia and Mr. Ramel. The system directly addresses this through a controlled environment with HEPA-filtered airflow. The AI component's goal of early contamination detection further reduces this risk.

#### Connectivity
As mentioned, the use of SQLite for offline functionality ensures the system remains operational during internet outages, a critical feature for agricultural technology in the Philippines.

### Core Algorithm Implementation

The M.A.S.H. system employs a **PID Controller with Adaptive Threshold Algorithm** as its primary control mechanism. This single, proven algorithm addresses all critical system requirements while maintaining technical simplicity and reliability.

#### PID Controller with Adaptive Thresholds
**Primary Algorithm**: Proportional-Integral-Derivative (PID) controller with dynamic threshold adjustment for temperature (25-28°C), humidity (80-90%), and CO₂ levels (10k-15k ppm).

**Algorithm Selection Rationale**:
1. **Proven Reliability**: PID controllers are industry-standard for environmental control systems
2. **Real-time Performance**: Provides immediate response to environmental changes (addresses Mr. Carcelia's climate concerns)
3. **Simple Implementation**: Feasible within ₱16,028 hardware budget using Raspberry Pi
4. **Adaptive Capability**: Dynamic thresholds adjust based on mushroom growth stages and seasonal variations
5. **Contamination Prevention**: Maintains precise environmental conditions that prevent contamination (primary stakeholder concern)

**Technical Implementation**:
```
PID Control Loop (250ms intervals):
1. Read sensor data (Temperature, Humidity, CO₂)
2. Calculate error from optimal setpoints
3. Apply PID formula: Output = Kp×Error + Ki×∫Error + Kd×(dError/dt)
4. Adjust actuators (humidifier, fans, ventilation)
5. Adapt thresholds based on growth stage and time patterns
```

**Algorithm Justification for M.A.S.H.**:
- **Addresses Environmental Inconsistency**: Replaces Mr. Ramel's "pakiramdam" approach with precise data-driven control
- **Prevents Contamination**: Maintains sterile conditions through consistent environmental management
- **Reduces Labor**: Automates the most labor-intensive monitoring tasks (Barangay 175 feedback)
- **Hardware Compatible**: Runs efficiently on Raspberry Pi Zero 2W with minimal processing overhead
- **Offline Capable**: Operates independently during internet outages using local processing

This single algorithm approach ensures system reliability, reduces complexity, and guarantees successful implementation within the project's technical and budget constraints while addressing all identified stakeholder needs.

## 3. Economical Feasibility
The project is economically viable for both the development phase and for potential end-users, demonstrating a clear path to a positive return on investment.

### Cost Breakdown
The detailed budget in the proposal lists the total hardware cost as ₱16,028.00. This is well within the team's working budget of ₱20,000, leaving ample room for contingencies, software subscriptions, and other project-related expenses. The cost is manageable and demonstrates responsible financial planning.

### Cost-Benefit & Return on Investment (ROI)
The economic benefits for a grower adopting the M.A.S.H. system are significant:

#### Increased Yield & Reduced Losses
The system directly combats the main causes of crop failure—environmental instability and contamination—which, according to stakeholders, are major issues, especially in the Philippine climate. Following the BPI expert's advice, a target yield increase of 20% is a measurable and achievable goal that would directly boost revenue.

#### Higher Profit Margins
Mr. Carcelia confirmed the large price disparity between the low "gate price" from wholesalers and the higher retail price. He stated that selling directly to consumers is the "best" way to maximize income. The integrated e-commerce platform facilitates this, bypassing middlemen and allowing growers to capture more of the final sale price.

#### Willingness to Invest
The most compelling evidence for the system's economic feasibility is Mr. Carcelia's confirmation that he would be willing to invest in the proposed device, viewing the prototype cost as reasonable for a small-scale operation. This serves as direct market validation for the product's value proposition.

### Sustainability of Funding
For the scope of the thesis, the project is fully funded by the team's budget. Beyond academia, the system's demonstrated ability to increase profitability for growers creates a sustainable business model where the initial investment in the M.A.S.H. device is recovered through improved sales and yields.

## Conclusion
The M.A.S.H. project demonstrates strong feasibility across all three domains. The operational analysis confirms user acceptance and workflow improvements, the technical assessment validates the chosen technology stack, and the economic evaluation shows clear paths to profitability. Stakeholder validation through interviews provides real-world confirmation of the system's potential impact on Philippine mushroom farming.