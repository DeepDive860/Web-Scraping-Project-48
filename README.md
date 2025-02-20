# U.S. Government Data Scraping Project

A collection of Scrapy spiders for extracting structured data from various U.S. government portals including:
- U.S. Census Bureau (census.gov)
- Government Publishing Office (govinfo.gov)
- Open Data Portal (data.gov)

## Features

- **Playwright Integration**: Handles JavaScript-rendered content and complex navigation
- **Pagination Handling**: Automatically follows "Next" buttons through multiple pages
- **Anti-blocking Measures**:
  - Rotating user-agents
  - Proxy rotation
  - Randomized delays
- **Data Extraction**:
  - PDF/XML resource links
  - Temporal metadata (years/months)
  - Dataset descriptions and metadata
  - Government document metadata

## Spiders Overview

| Spider Name                          | Target Website     | Data Collected                                                                 |
|--------------------------------------|--------------------|--------------------------------------------------------------------------------|
| `ManufacturingandTradeInventoriesandSales` | census.gov         | Historical inventory reports with year/month/file links                       |
| `uspresedentialdocument`             | govinfo.gov        | Presidential documents with PDF links and metadata                            |
| `usdataset`                          | data.gov           | Open dataset metadata (300K+ records)                                         |
| `usinfo`                             | govinfo.gov        | Government publications from multiple collections                             |
| `usgovinfo`                          | govinfo.gov        | Detailed budget documents with nested hierarchy parsing                       |

## Installation

1. **Prerequisites**:
   ```bash
   python -m pip install scrapy scrapy-playwright
   python -m playwright install

Clone Repository:

git clone https://github.com/DeepDive860/government-data-scrapers.git
cd government-data-scrapers

This project contains extracted JSON data from various U.S. government sources, including:

Census.gov (censusgov.json): Data related to population, demographics, and economic statistics.
Compilation of Presidential Documents (compilationofpresedentialdocument.json): Official presidential statements, speeches, and executive orders.
U.S. Government Information (usgovernmentinformation.json): Various publicly available records from government agencies.
U.S. Gov Info (usgovinfo.json): Additional datasets covering different aspects of federal operations.
Large Dataset Note
The DataGov dataset contains over 300,000+ records, but due to GitHub's 50MB file size limit, it is not included in this repository.

