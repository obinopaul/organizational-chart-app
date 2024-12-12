function renderHomepageCharts(ubrLevelData) {
    // Check if the data is in the correct format
    console.log("Filtered ubrLevelData:", ubrLevelData);

    Object.keys(ubrLevelData).forEach((ubrLevel, index) => {
        const data = ubrLevelData[ubrLevel]?.employees || []; // Ensure employees data is fetched correctly
        const totalCount = ubrLevelData[ubrLevel]?.total_count || 0; // Fetch total employee count
        const validEmployeeIds = new Set(ubrLevelData[ubrLevel]?.employee_ids || []);  // Set of valid employee IDs for this group


        // Log if no employees exist for a level
        if (data.length === 0) {
            console.warn(`No employees found for UBR level: ${ubrLevel}`);
            return; // Skip rendering for this level if no employees are present
        }

        // Guard rail: Ensure that the data only includes employees for the current UBR level
        const filteredData = data.filter(d => d['UBR Level 8'] === ubrLevel);

        // Log if filtering the employees for the level results in an empty array
        if (filteredData.length === 0) {
            console.warn(`No employees found for UBR level: ${ubrLevel} after filtering.`);
            return; // Skip rendering if no employees are found after filtering
        }

        // Define the container for each mini chart
        const containerId = `#mini-chart-${index + 1}`;
        const container = d3.select(containerId);

        // Set flexible height based on the number of directors
        const individualHeight = 120;  // Increased height for better spacing
        const chartHeight = Math.max(individualHeight, individualHeight * Math.ceil(filteredData.length / 2));
        const width = 350;  // Slightly wider for better spacing

        // If no Managing Director or Director is available, display message
        if (filteredData.length === 0) {
            container.append("p").text("No Managing Director or Director available.");
            return;
        }

        // Set up mini chart SVG with dynamic height
        const svg = container.append("svg")
            .attr("width", width)
            .attr("height", chartHeight);

        // Filter the employees to ensure only valid IDs are placed in this group
        // const validData = data.filter(d => validEmployeeIds.has(d['Employee ID']));

        // Add defs for profile images as patterns
        svg.selectAll("defs")
            .data(filteredData)
            .enter()
            .append("defs")
            .append("pattern")
            .attr("id", d => `img-${d['Employee ID']}`)
            .attr("patternUnits", "objectBoundingBox")
            .attr("width", 1)
            .attr("height", 1)
            .append("image")
            .attr("xlink:href", d => d['profile_image'] || "/static/img/dummy-profile.png")  // Replace with actual URL or default
            .attr("width", 60)
            .attr("height", 60)
            .attr("x", -10)
            .attr("y", -10);

        // Filter the employees to ensure only valid IDs are placed in this group
        const validData = filteredData.filter(d => validEmployeeIds.has(d['Employee ID']));

        // // Set up circle and rectangle layout for Managing Director and Directors
        // const nodeGroup = svg.selectAll(".node")
        //     .data(validData)
        //     .enter()
        //     .append("g")
        //     .attr("class", "node")
        //     .attr("transform", (d, i) => `translate(${60 + (i % 2) * 150}, ${Math.floor(i / 2) * individualHeight + 30})`);


        // Set up circle and rectangle layout for Managing Director and Directors
        const nodeGroup = svg.selectAll(".node")
            .data(validData)
            .enter()
            .append("g")
            .attr("class", "node")
            .attr("transform", (d, i) => {
                // Check if the employee is in the correct UBR level before placing them
                if (d['UBR Level 8'] !== ubrLevel) {
                    console.warn(`Employee ${d['Preferred Name']} skipped. UBR level mismatch.`);
                    return "";  // Skip rendering if the UBR level doesn't match
                }

                // Only proceed if the UBR level matches
                return `translate(${60 + (i % 2) * 150}, ${Math.floor(i / 2) * individualHeight + 30})`;
            });

        // Circle for profile picture using pattern
        nodeGroup.append("circle")
            .attr("r", 30)
            .attr("fill", d => `url(#img-${d['Employee ID']})`)
            .attr("stroke", "#ccc")
            .attr("stroke-width", "2");

        // Rectangle for name and title
        nodeGroup.append("rect")
            .attr("x", -60)
            .attr("y", 40)
            .attr("width", 120)
            .attr("height", 45)
            .attr("fill", "#D4A373")
            .attr("rx", 10)
            .attr("ry", 10);

        // Name text
        nodeGroup.append("text")
            .attr("dy", 55)
            .attr("text-anchor", "middle")
            .attr("class", "name")
            .text(d => d['Preferred Name'])
            .attr("fill", "white")
            .attr("font-weight", "bold");

        // Title text
        nodeGroup.append("text")
            .attr("dy", 75)
            .attr("text-anchor", "middle")
            .attr("class", "title")
            .text(d => d['Worker Corporate Title'])
            .attr("fill", "white");

        // Tooltip on hover
        nodeGroup.on("mouseover", function(event, d) {
            const tooltip = d3.select("body")
                .append("div")
                .attr("class", "tooltip")
                .style("position", "absolute")
                .style("background", "linear-gradient(135deg, #FFD700, #FF8C00)")
                .style("border-radius", "8px")
                .style("padding", "12px")
                .style("color", "#333")
                .style("font-size", "14px")
                .style("box-shadow", "0px 4px 8px rgba(0, 0, 0, 0.2)")
                .style("left", `${event.pageX + 15}px`)
                .style("top", `${event.pageY + 15}px`)
                .html(`
                    <p><strong>${d['Preferred Name']}</strong></p>
                    <p>Employee ID: ${d['Employee ID']}</p>
                    <p>Email: ${d['Email - Work']}</p>
                    <p>Title: ${d['Worker Corporate Title']}</p>
                    <p>City: ${d['Location Address - City']}</p>
                    <p>Cost Center: ${d['Cost Center Name']}</p>
                    <p>Manager: ${d['Organization Manager']}</p>
                    <p>Division (UBR Level): ${ubrLevel}</p>  <!-- Display the UBR level here as the division -->
            `);
        }).on("mousemove", function(event) {
            d3.select(".tooltip")
                .style("left", `${event.pageX + 15}px`)
                .style("top", `${event.pageY + 15}px`);
        }).on("mouseout", function() {
            d3.select(".tooltip").remove();
        });
    });
}
