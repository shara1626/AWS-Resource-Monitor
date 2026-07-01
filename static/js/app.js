// Function to fetch AWS resource data

async function fetchResources() {
console.log("Refreshing dashboard...", new Date().toLocaleTimeString());

 const response = await fetch("/api/resources");
 const data = await response.json();
 
 const tableBody = document.getElementById("ec2-table-body");
 tableBody.innerHTML = "";

data.ec2.forEach(function(instance) {

    tableBody.innerHTML += `
        <tr>
            <td>${instance.id}</td>
            <td>${instance.type}</td>
            <td class="${instance.state}">${instance.state}</td>
            <td>${instance.public_ip}</td>
            <td>${instance.region}</td>
        </tr>
    `;

});

 document.getElementById("ec2-count").textContent = data.ec2.length;
 document.getElementById("s3-count").textContent = data.s3.length;
 document.getElementById("rds-count").textContent = data.rds.length;
 document.getElementById("lambda-count").textContent = data.lambda.length;

 data.ec2.forEach(function(instance) {

   console.log("ID:", instance.id);

   console.log("State:", instance.state);

   console.log("Type:", instance.type);
   
   console.log("----------------------");
 });

}
// Run once immediately
fetchResources();

// Refresh every 30 seconds
setInterval(fetchResources, 30000);
