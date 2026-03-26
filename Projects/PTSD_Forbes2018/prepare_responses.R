# prepare_responses.R
# Downloads Forbes (2018) raw data from OSF and writes responses.csv
# for the items listed in items.csv (PHQ-9 only).
#
# Run this before diagnosis if responses.csv is missing:
#   Rscript Projects/PTSD_Forbes2018/prepare_responses.R

library(osfr)

project_folder <- "Projects/PTSD_Forbes2018"
raw_path       <- "Data/PTSD/time1and2data_wide.csv"

# Download raw data if not already present
if (!file.exists(raw_path)) {
  dir.create("Data/PTSD", recursive = TRUE, showWarnings = FALSE)
  forbes2018       <- osf_retrieve_node("https://osf.io/6fk3v/")
  forbes2018_files <- osf_ls_files(forbes2018)
  osf_download(forbes2018_files[7, ], path = "Data/PTSD", conflicts = "skip")
}

raw <- read.csv(raw_path, header = FALSE)

# Time 1 columns 2-17 contain PHQ1-9 and GAD1-7
all_items <- setNames(
  as.data.frame(raw[, 2:17]),
  c(paste0("PHQ", 1:9), paste0("GAD", 1:7))
)

# Select only items listed in items.csv
items     <- read.csv(file.path(project_folder, "items.csv"))
item_ids  <- items$item_id
responses <- all_items[, item_ids]

write.csv(responses, file.path(project_folder, "responses.csv"), row.names = FALSE)
message("Saved: ", file.path(project_folder, "responses.csv"),
        " (", nrow(responses), " persons x ", ncol(responses), " items)")
