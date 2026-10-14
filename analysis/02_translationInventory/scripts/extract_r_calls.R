# Run inside the R reference image. Lists every function call in the EWARS model's R scripts,
# from R's own parser (getParseData), so that "every R call" is a mechanical list rather than
# a reading. Each call is resolved to what supplies it at runtime, after loading the packages
# the scripts load, in their order. Also lists the f(...) terms written inside the formula
# strings, which the parser sees only as string constants.
#
# Usage (in the image): Rscript extract_r_calls.R <scripts_dir> <out_tsv>
args <- commandArgs(trailingOnly = TRUE)
src_dir <- args[1]; out <- args[2]
files <- c("predict.R", "lib.R", "train.R")

suppressPackageStartupMessages({
  library(yaml); library(jsonlite); library(INLA); library(dlnm); library(dplyr)
  library(sf); library(spdep)
})

rows <- list()
local_defs <- character()
for (f in files) {
  pd <- getParseData(parse(file.path(src_dir, f), keep.source = TRUE))
  # functions the scripts define themselves: SYMBOL followed by an assignment of `function`
  syms <- pd[pd$token == "SYMBOL", ]
  for (i in seq_len(nrow(syms))) {
    nxt <- pd[pd$line1 == syms$line1[i] & pd$col1 > syms$col1[i] & pd$terminal, ]
    nxt <- nxt[order(nxt$col1), ]
    if (nrow(nxt) >= 2 && nxt$token[1] == "LEFT_ASSIGN" && nxt$token[2] == "FUNCTION")
      local_defs <- c(local_defs, syms$text[i])
  }
  calls <- pd[pd$token == "SYMBOL_FUNCTION_CALL", ]
  for (i in seq_len(nrow(calls)))
    rows[[length(rows) + 1]] <- data.frame(file = f, line = calls$line1[i], call = calls$text[i],
                                           kind = "call", stringsAsFactors = FALSE)
  strs <- pd[pd$token == "STR_CONST" & grepl("f\\(", pd$text), ]
  for (i in seq_len(nrow(strs))) {
    terms <- regmatches(strs$text[i], gregexpr("f\\([^)]*\\)", strs$text[i]))[[1]]
    for (t in terms)
      rows[[length(rows) + 1]] <- data.frame(file = f, line = strs$line1[i], call = t,
                                             kind = "formula-term", stringsAsFactors = FALSE)
  }
}
calls <- do.call(rbind, rows)

resolve <- function(fn, kind) {
  if (kind == "formula-term") return("INLA (formula)")
  if (fn %in% local_defs) return("local")
  where <- find(fn)
  if (length(where) == 0) return("UNRESOLVED")
  paste(sub("^package:", "", where), collapse = ";")
}
calls$supplied_by <- mapply(resolve, calls$call, calls$kind)
calls <- calls[order(calls$file, calls$line, calls$call), ]
write.table(calls, out, sep = "\t", quote = FALSE, row.names = FALSE)
cat(nrow(calls), "call sites,", length(unique(calls$call)), "distinct; local functions:",
    paste(unique(local_defs), collapse = ", "), "\n")
