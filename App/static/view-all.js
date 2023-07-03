window.onload = function(){
    let deleteBtn = document.getElementsByClassName("item-delete");

    for(let i = 0; i < deleteBtn.length; i++){
        deleteBtn[i].onclick = function(e){
            if(!confirm("Are you sure?")){
                e.preventDefault()
            }
        }
        
    }

    let parsed = JSON.parse(items)

    // parsed.forEach(p => {
    //     p.prices = p.prices.map(i => ({date: new Date(i.date), price: i.price}))
    // })

    parsed.forEach(p => {
        let item = document.getElementById(p.id)
        let recent = p.prices.reduce((a, b) => (a.date > b.date ? a : b))
        item.append(recent.price.toFixed(2))
    })







}