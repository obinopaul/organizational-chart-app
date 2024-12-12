
function renderManagementChart(data) {
    // Dynamic sizing based on number of employees
    const minNodeSpacing = 200; // Minimum horizontal space between nodes
    const levelHeight = 280; // Increased vertical space between levels
    const nodeRadius = 40;
    const labelHeight = 60;
    
    // Define title hierarchy levels
    const titleLevels = {
        "Managing Director": 1,
        "Director": 2,
        "Vice President": 3,
        "Assistant Vice President": 4,
        "Associate": 5,
        "Analyst": 6
    };

    // Group all employees by their title level
    const levelGroups = {
        1: [], 2: [], 3: [], 4: [], 5: [], 6: []
    };

    data.forEach(emp => {
        const level = titleLevels[emp['Worker Corporate Title']];
        if (level) {
            levelGroups[level].push(emp);
        }
    });

    // Calculate dimensions based on maximum number of employees in any level
    const maxNodesInLevel = Math.max(...Object.values(levelGroups).map(g => g.length));
    const width = Math.max(maxNodesInLevel * minNodeSpacing, 1200); // Ensure minimum width
    const height = (7 * levelHeight); // 6 levels plus extra space

    // Position each employee horizontally within their level
    Object.entries(levelGroups).forEach(([level, employees]) => {
        if (employees.length === 0) return;

        // Calculate horizontal spacing for this level
        const levelWidth = width - 200; // Account for margins
        const effectiveWidth = Math.max(levelWidth, employees.length * minNodeSpacing);
        const spacing = effectiveWidth / (employees.length + 1);

        // Position each employee in the level
        employees.forEach((emp, index) => {
            emp.x = ((index + 1) * spacing);
            emp.y = (level - 1) * levelHeight + 100;
        });
    });

    // Create employee ID map for easier lookups
    const employeeMap = {};
    data.forEach(emp => {
        employeeMap[emp['Employee ID']] = emp;
    });

    // Set up SVG with dynamic dimensions
    const svg = d3.select("#chart")
        .append("svg")
        .attr("width", width + 400) // Extra padding for wide charts
        .attr("height", height + 200)
        .append("g")
        .attr("transform", "translate(200, 50)"); // Increased left margin


    // Draw links between employees and their managers
    const links = [];
    data.forEach(emp => {
        const managerId = emp['Organization Manager Employee ID'];
        if (managerId && employeeMap[managerId]) {
            links.push({
                source: employeeMap[managerId],
                target: emp
            });
        }
    });

    // Render links with smoother curves
    svg.selectAll(".link")
        .data(links)
        .enter()
        .append("path")
        .attr("class", "link")
        .attr("d", d => {
            const sourceX = d.source.x;
            const sourceY = d.source.y;
            const targetX = d.target.x;
            const targetY = d.target.y;
            
            // Calculate control points for smoother curves
            const midY = (sourceY + targetY) / 2;
            
            return `M${sourceX},${sourceY}
                    C${sourceX},${midY}
                     ${targetX},${midY}
                     ${targetX},${targetY}`;
        })
        .attr("fill", "none")
        .attr("stroke", "#ccc")
        .attr("stroke-width", 2);

    // Render all employees as nodes
    const nodes = svg.selectAll(".node")
        .data(data)
        .enter()
        .append("g")
        .attr("class", "node")
        .attr("transform", d => `translate(${d.x}, ${d.y})`);

    // Add background circle for better visibility
    nodes.append("circle")
        .attr("r", nodeRadius + 2)
        .attr("fill", "white")
        .attr("stroke", "#333")
        .attr("stroke-width", 2);

    // Render circles for nodes
    nodes.append("circle")
        .attr("r", nodeRadius)
        .attr("fill", d => `url(#img-${d['Employee ID']})`)
        .attr("stroke", "#333")
        .attr("stroke-width", 2);

    // Highlight the specific node based on the query parameter
    const urlParams = new URLSearchParams(window.location.search);
    const highlightId = urlParams.get('highlight'); // Get the highlight parameter

    // Render rectangles for names and titles with increased spacing
    nodes.append("rect")
        .attr("x", -60)
        .attr("y", nodeRadius + 5)
        .attr("width", 120)
        .attr("height", labelHeight)
        // .attr("fill", "#D4A373")
        .attr("fill", d => d['Employee ID'] === highlightId ? "#FF6347" : "#D4A373") // Change color for highlighted employee
        .attr("rx", 10)
        .attr("ry", 10);

    // Add names with better spacing
    nodes.append("text")
        .attr("dy", nodeRadius + 25)
        .attr("text-anchor", "middle")
        .attr("class", "employee-name")
        .text(d => d['Preferred Name'])
        .attr("fill", "white");

    // Add titles with better spacing
    nodes.append("text")
        .attr("dy", nodeRadius + 45)
        .attr("text-anchor", "middle")
        .attr("class", "employee-title")
        .text(d => d['Worker Corporate Title'] === "Assistant Vice President" 
            ? "Assistant VP" 
            : d['Worker Corporate Title'])
        .attr("fill", "white");

    // Profile images
    svg.append("defs").selectAll("pattern")
        .data(data)
        .enter()
        .append("pattern")
        .attr("id", d => `img-${d['Employee ID']}`)
        .attr("patternUnits", "objectBoundingBox")
        .attr("width", 1)
        .attr("height", 1)
        .append("image")
        .attr("xlink:href", d => d['profile_image'] || "/static/img/dummy-profile.png")
        .attr("width", nodeRadius * 2)
        .attr("height", nodeRadius * 2)
        .attr("x", 0)
        .attr("y", 0);

    if (highlightId) {
        nodes.filter(d => d['Employee ID'] === highlightId)
            .select("circle")
            .attr("stroke", "red") // Highlight border
            .attr("stroke-width", 4); // Increase border width
    }
    // Enhanced tooltips
    nodes.on("mouseover", function(event, d) {
        const manager = employeeMap[d['Organization Manager Employee ID']];
        const matrixManager = d['Matrix Manager'] || "No Matrix Manager";

        d3.select("body").append("div")
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
                <hr>
                <p><strong>Direct Manager:</strong> ${d['Organization Manager']}</p>
                <p>Manager ID: ${d['Organization Manager Employee ID']}</p>
                <p><strong>Matrix Manager:</strong> ${d['Matrix Manager']}</p>
            `);
    }).on("mousemove", function(event) {
        d3.select(".tooltip")
            .style("left", `${event.pageX + 15}px`)
            .style("top", `${event.pageY + 15}px`);
    }).on("mouseout", function() {
        d3.select(".tooltip").remove();
    });

}