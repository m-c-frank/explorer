marked.use({
	headerIds: false,
	mangle: false,
});

document.addEventListener('DOMContentLoaded', async function () {
	nodes = []
	edges = []
	await fetch('/data/nodes').then(function (response) {
		return response.json();
	}).then(function (data) {
		nodes = data
	});
	await fetch('/data/edges').then(function (response) {
		return response.json();
	}).then(function (data) {
		edges = data
	});

	makeGraph({ "nodes": nodes, "edges": edges })
});

function jsonToMarkdown(obj, level = 1) {
	let markdown = '';
	for (let key in obj) {
		markdown += `${'#'.repeat(level)} ${key}\n\n`;
		if (typeof obj[key] === 'object') {
			markdown += jsonToMarkdown(obj[key], level + 1);
		} else {
			markdown += obj[key]
			markdown += "\n\n"
		}
	}
	return markdown;
}

function viewNode(node) {
	let markdown_node = jsonToMarkdown(node);
	let htmlContent = marked.parse(markdown_node);
	document.getElementById("markdown").innerHTML = htmlContent
	return
}

function getDisplayContent(content) {
	let preview = content.substring(0, 256)
	let htmlContent = marked.parse(preview)
	return htmlContent
}

function makeGraph(graphData) {
	var element = document.getElementById("graph");
	var width = element.offsetWidth;
	var height = element.offsetHeight;

	const svg = d3.create("svg")
		.attr("width", width)
		.attr("height", height)
		.attr("viewBox", [-width / 2, -height / 2, width, height])
		.attr("style", "max-width: 100%; height: auto;");

	const g = svg.append("g");
	const zoom = d3.zoom()
		.scaleExtent([0.1, 8])  // This defines the limit for zooming in and out
		.on("zoom", (event) => {
			g.attr("transform", event.transform); // This updates the transform attribute of g based on the zoom
		});

	// Apply the zoom behavior to the svg
	svg.call(zoom);

	var tooltip = d3.select("body").append("div")
		.attr("class", "tooltip")
		.style("opacity", 0);

	var nodes = graphData.nodes
	var links = graphData.edges

	const simulation = d3.forceSimulation(nodes)
		.force("link", d3.forceLink(links).id(d => d.id))
		.force("charge", d3.forceManyBody())
		.force("x", d3.forceX())
		.force("y", d3.forceY());

	var link = g.append("g")
		.attr("class", "links")
		.selectAll("line")
		.data(links)
		.enter().append("line")
		.attr("stroke-width", 1);

	var node = g.append("g")
		.style("fill", "#fff")
		.style("stroke", "#0f0")
		.style("stroke-width", "1.5px")
		.selectAll("circle")
		.data(nodes)
		.enter().append("circle")
		.attr("r", 5)
		.on("click", function (event, d) {
			console.log("Clicked node", d);
			viewNode(d)
		})
		.on("mouseover", function (event, d) {
			tooltip.transition()
				.duration(200)
				.style("opacity", .9);
			tooltip.html(d)
				.style("left", (event.pageX) + "px")
				.style("top", (event.pageY - 28) + "px");
		})
		.on("mouseout", function (event, d) {
			tooltip.transition()
				.duration(500)
				.style("opacity", 0);
		});

	node.classed("phantomnode", function (d) { return d.content == ""; });

	node.call(d3.drag()
		.on("start", dragstarted)
		.on("drag", dragged)
		.on("end", dragended));

	simulation.on("tick", function () {
		link.attr("x1", d => d.source.x)
			.attr("y1", d => d.source.y)
			.attr("x2", d => d.target.x)
			.attr("y2", d => d.target.y);

		node.attr("cx", d => d.x)
			.attr("cy", d => d.y);
	});

	function dragstarted(event) {
		if (!event.active) simulation.alphaTarget(0.3).restart();
		event.subject.fx = event.subject.x;
		event.subject.fy = event.subject.y;
	}

	function dragged(event) {
		event.subject.fx = event.x;
		event.subject.fy = event.y;
	}

	function dragended(event) {
		if (!event.active) simulation.alphaTarget(0);
		event.subject.fx = null;
		event.subject.fy = null;
	}
	element.appendChild(svg.node());
};
