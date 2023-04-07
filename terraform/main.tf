  terraform {
    required_version = ">= 1.0"
    backend "local" {}  
    required_providers {
      google = {
        source  = "hashicorp/google"
      }
    }
  }

provider "google" {
  project = var.project
  region = var.region
}

resource "google_storage_bucket" "data-lake-bucket" {
name          = "${local.data_lake_bucket}_${var.project}" # Concatenating DL bucket & Project name for unique naming
location      = var.region

# Optional settings:
storage_class = var.storage_class
uniform_bucket_level_access = true

versioning {
  enabled     = true
}

lifecycle_rule {
  action {
    type = "Delete"
  }
  condition {
    age = 30  // days
  }
}

force_destroy = true
}

resource "google_bigquery_dataset" "dataset" {
dataset_id = var.BQ_DATASET
project    = var.project
location   = var.region
}

resource "google_bigquery_table" "cycling_table" {
  dataset_id = var.BQ_DATASET
  table_id   = "cycling_table"

  schema = <<EOF
  [
    {
      "name": "Rental_Id",
      "type" : "STRING",
      "mode" : "NULLABLE"

    },
    {
      "name": "Bike_Id",
      "type" : "STRING",
      "mode" : "NULLABLE"
     
    },
    {
      "name": "End_Date",
      "type" : "TIMESTAMP",
      "mode" : "NULLABLE"
  
    },
    {
      "name": "EndStation_Id",
      "type" : "STRING",
      "mode" : "NULLABLE"
    
    },
    {
      "name": "EndStation_Name",
      "type" : "STRING",
      "mode" : "NULLABLE"
    
    },
    {
      "name": "Start_Date",
      "type" : "TIMESTAMP",
      "mode" : "NULLABLE"
   
    },
    {
      "name": "StartStation_Id",
      "type" : "STRING",
      "mode" : "NULLABLE"
   
    },
    {
      "name": "StartStation_Name",
      "type" : "STRING",
      "mode" : "NULLABLE"
   
    },
    {
      "name": "Duration",
      "type": "INTEGER",
      "mode": "NULLABLE"
    }

  ] 
  EOF  
}