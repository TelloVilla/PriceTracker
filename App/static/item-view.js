
window.onload = function(){

    const itemPrices = JSON.parse(item_prices)

    const timeFormat = d3.timeParse("%Y-%m-%d")

    const formatedPrices = itemPrices.map(p => ({pid: p.pid, date: timeFormat(p.date), value: p.price}))

    console.log(formatedPrices)

    formatedPrices.sort(function(a, b){
        return a.date - b.date;
    })
    
    const display = d3.select("#price-display")
    .append("svg")
        .attr("width", 700)
        .attr("height", 500)
    .append("g")
        .attr("transform", "translate(50, 20)")

    const x = d3.scaleTime()
        .domain(d3.extent(formatedPrices, function(d){return d.date;}))
        .range([0, 600])
    display.append("g")
        .attr("transform", "translate(0, 400)")
        .call(d3.axisBottom(x));

    const y = d3.scaleLinear()
        .domain([0, d3.max(formatedPrices, function(d){return +d.value;})])
        .range([400, 0])
    display.append("g")
        .call(d3.axisLeft(y))

    const valueLine = d3.line()
        .x(function(d){return x(d.date)})
        .y(function(d){return y(d.value)})


    display.append("path")
        .datum(formatedPrices)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 2.5)
        .attr("d", d3.line()
            .x(d => x(d.date))
            .y(d => y(d.value))
            
        )
        .on("click", function(e, d){
            console.log(d)
        })

    display.selectAll("circle")
        .data(formatedPrices).enter()
        .append("circle")
        .attr("fill", "steelblue")
        .attr("cx", d=> x(d.date))
        .attr("cy", d=> y(d.value))
        .attr("r", "5px")
        .on("mouseover", function(e, d){
            tipX = e.pageX
            tipY = e.pageY
            d3.select(this)
            .attr("fill", "red")
            d3.select(".graphtip")
            .html("<span>Price: " + d.value + "<br>Date: " + d.date.toDateString() + "</span>")
            .style("visibility", "visible")
            .style("left", tipX + 10 + "px")
            .style("top", tipY + 10 + "px")
        })
        .on("click", function(e,d){
            d3.select(".offcanvas")
            .classed("show", true)
            
            
            d3.select("#price-edit")
            .property("value", d.value)

            d3.select("#priceid")
            .property("value", d.pid)
        })
        .on("mouseleave", function(e, d){
            d3.select(this)
            .attr("fill", "steelblue")

            d3.select(".graphtip")
            .style("visibility", "hidden")
        })

        d3.select(".btn-close")
        .on("click", function(e){
            d3.select(".offcanvas")
            .classed("show", false)
        })

        let priceTotal = 0;
        formatedPrices.forEach(p => priceTotal += +p.value)

        price_avg = priceTotal / formatedPrices.length

        d3.select("#price-avg")
        .text(price_avg.toFixed(2))

}

