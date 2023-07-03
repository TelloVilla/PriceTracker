window.onload = function(){
    let listSelectors = document.getElementsByClassName("show-class")

    let prices = document.getElementsByClassName("item-price")

    for(let p = 0; p < prices.length; p++){
        prices[p].value = Number(prices[p].value).toFixed(2)
    }
    
    let total = 0;

    parsedLists = JSON.parse(Lists)

    parsedLists.forEach(l =>{
        listTotal = 0;
        for(let p = 0; p < prices.length; p++){
            if(prices[p].id == l.id){
                listTotal += +prices[p].value
            }
        }
        let totalEle = document.getElementById(l.id + "-total-price");
        totalEle.append(listTotal.toFixed(2))
    })

    

    
        
    
}