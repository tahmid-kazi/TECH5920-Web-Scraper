let reports_index; // This is the json object containing the reports

fetch('reports_index.json')
    .then(response => response.json())
    .then(data => {
        reports_index = data;
        console.log("Featching reports successful");
        updateReports();
    })
    .catch(error => console.error('Error fetching the reports index JSON file:', error));

function updateReports(){
    const reportElement = document.getElementById('reports');
    // first clear the list
    while (reportElement.firstChild) {
        reportElement.removeChild(reportElement.firstChild);
    }
    // then append with new product feature list
    for (let i=0; i < reports_index.reports.length; i++){
        const reportEntry = document.createElement('li')
        reportEntry.textContent = reports_index.reports[i].name;
        // Add click event listener to each list item
        reportEntry.addEventListener('click', () => {
          showReportContent(reports_index.reports[i].filename);
        });

        reportElement.appendChild(reportEntry);
    }
}

function showReportContent(filename) {
    let reports_content;
    const reportContentElement = document.getElementById('report_content');
    // first clear the list
    while (reportContentElement.firstChild) {
      reportContentElement.removeChild(reportContentElement.firstChild);
    }

    fetch(filename)
      .then(response => response.json())
      .then(data => {
          reports_content = data;
          console.log("Featching reports content successful");

          // Create a heading element for the summary
      const summaryHeading = document.createElement('h2');
      summaryHeading.textContent = 'Summary';
      reportContentElement.appendChild(summaryHeading);

      // Create a paragraph element for the summary text
      const summaryParagraph = document.createElement('p');
      summaryParagraph.textContent = reports_content.summary;
      reportContentElement.appendChild(summaryParagraph);

      // Create a heading element for the sources
      const sourcesHeading = document.createElement('h2');
      sourcesHeading.textContent = 'Sources';
      reportContentElement.appendChild(sourcesHeading);

      // Create an unordered list for the sources
      const sourcesList = document.createElement('ul');

      // Add each source as a list item with a clickable link
      reports_content.sources.forEach(source => {
        const sourceItem = document.createElement('li');
        const sourceLink = document.createElement('a');
        sourceLink.href = source.url;
        sourceLink.target = '_blank'; // Open links in a new tab/window
        sourceLink.textContent = source.title;
        sourceItem.appendChild(sourceLink);
        sourcesList.appendChild(sourceItem);
      });

      reportContentElement.appendChild(sourcesList);
      })
      .catch(error => console.error('Error fetching the reports content JSON file:', error));

}