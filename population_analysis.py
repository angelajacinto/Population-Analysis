import pandas as pd

def load (csvfile):
    """Loads CSV file and extracts relevant columns into lists"""
    infile = open(csvfile, "r") 
    list_country= [] 
    list_population = [] 
    list_net_change = [] 
    list_land_area = [] 
    list_regions = []

    # Read the header to get column indices
    header = infile.readline().strip().split(",")
    index_map = {col.strip(): i for i, col in enumerate(header)}
        
    for line in infile:
        row = line.strip().split(",")
        list_country.append(row[index_map["Country"]])
        list_population.append(row[index_map["Population"]])
        list_net_change.append(row[index_map["Net Change"]])
        list_land_area.append(row[index_map["Land Area"]])
        list_regions.append(row[index_map["Regions"]])
        
    return list_country, list_population, list_net_change, list_land_area, list_regions
        
def get_region_indices (region, regions): 
    """Returns a list of indices where the region matches the given region name."""
    result = []
    
    for i in range (1, len(regions)): #for the whole column of region
        #print(regions[i].lower().strip())
        if regions[i].lower().strip() == region.lower().strip(): #if it is equal to specific region
            result.append(i)
            
    return result

def compute_standard_error (indices, populations):
    """Calculates the standard error of population values for a given region."""
    a = 0 
    for i in indices:
        a = a + int(populations[i]) 
    average = a / len(indices)
    
    b = 0
  
    for i in indices:
       
        b = b + ((int(populations[i]) - average)**2)
       
    
    stdv = (b / (len(indices)-1)) ** (1 / 2)
    stderr = stdv / (len(indices) **(1/2))
   
    return (float("{:.4f}".format(stderr)))

def compute_cosine_similarity (indices, populations, list_land_area):
    ab = 0
    a2 = 0
    b2 = 0
    for i in indices:
        ab = ab + (int(populations[i]) * int(list_land_area[i]))
        a2 = a2 + (int(populations[i])**2)
        b2 = b2 + (int(list_land_area[i])**2)
    
    return (ab / ((a2**(1/2)) * (b2**(1/2))) )       
        
def generate_region_statistics(list_regions, list_country, list_population, list_land_area):
    """Creates a dictionary with region-level statistics (standard error and cosine similarity)."""
    region_stats = {}
    for region in set(map(str.lower, list_regions)):
        indices = get_region_indices(region, list_regions)
        region_stats[region] = [
            compute_standard_error(indices, list_population),
            compute_cosine_similarity(indices, list_population, list_land_area)
        ]
    return region_stats

def total_sum(indices, list_population):
    """Calculates the total population for a given region."""
    a = 0
    for i in indices:
        a = a + int(list_population[i])
    return a

def generate_country_statistics(list_regions, list_population, list_land_area, list_net_change, list_country):
    """Creates a nested dictionary with country statistics categorized by region."""
    country_stats = {}
    for region in set(map(str.lower, list_regions)):
        indices = get_region_indices(region, list_regions)
        total_population = sum(int(list_population[i]) for i in indices)
        
        countries = [
            [list_country[i].lower().strip(),
             round(int(list_population[i]) / int(list_land_area[i]), 4),  # Density
             int(list_population[i])]
            for i in indices
        ]
        
        countries.sort(key=lambda x: (x[2], x[1]), reverse=True)  # Sort by population then density
        ranking = {country[0]: rank + 1 for rank, country in enumerate(countries)}
        
        country_stats[region] = {
            list_country[i].lower().strip(): [
                int(list_population[i]), int(list_net_change[i]),
                round((int(list_population[i]) / total_population) * 100, 4),
                round(int(list_population[i]) / int(list_land_area[i]), 4),
                ranking[list_country[i].lower().strip()]
            ]
            for i in indices
        }
    return country_stats
                    
def clean_data(df):
    """
    Cleans the dataset by:
    - Removing duplicate countries
    - Removing invalid population, land area, and region values
    """
    df = df.drop_duplicates(subset=["Country"], keep="first")
    df["Population"] = pd.to_numeric(df["Population"], errors="coerce")
    df["Net Change"] = pd.to_numeric(df["Net Change"], errors="coerce")
    df["Land Area"] = pd.to_numeric(df["Land Area"], errors="coerce")
    df = df.dropna()
    df = df[(df["Population"] > 0) & (df["Land Area"] > 0)]
    
    return df

def main(csvfile):
    """Main function to process the CSV file and return region and country statistics."""
    list_country, list_population, list_net_change, list_land_area, list_regions = load(csvfile)
    region_stats = generate_region_statistics(list_regions, list_country, list_population, list_land_area)
    country_stats = generate_country_statistics(list_regions, list_population, list_land_area, list_net_change, list_country)
    return region_stats, country_stats