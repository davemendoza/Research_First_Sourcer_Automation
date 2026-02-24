console.log("Talent Intelligence Command Console Max Ceiling Ready")

async function runQuery(vector){

    const response = await fetch("/api/query",{

        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            embedding:vector
        })
    })

    const data = await response.json()

    console.log("Results:",data)
}
