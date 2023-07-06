window.onload = function(){

    let prices = document.getElementsByClassName("item-price")

    for(let p = 0; p < prices.length; p++){
        prices[p].value = Number(prices[p].value).toFixed(2)
    }
    
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

    let deleteBtns = document.getElementsByClassName("list-delete")

    for(let i = 0; i < deleteBtns.length; i++){
        deleteBtns[i].onclick = function(e){
            if(!confirm("Are you sure?")){
                e.preventDefault()
            }
        }
        
    }

    let noteBtns = document.getElementsByClassName("item-note")

    console.log(noteBtns)

    for(let i = 0; i < noteBtns.length; i++){
        noteBtns[i].onclick = function(e){
            let noteForm = document.getElementById("note-form")
            noteForm.action = "/lists/" + noteBtns[i].dataset.listId + "/notes/" + noteBtns[i].dataset.itemId
        }
    }

    

    
        
    
}