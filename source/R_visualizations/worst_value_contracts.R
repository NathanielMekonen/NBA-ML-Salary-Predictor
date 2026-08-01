library(tidyverse)
library(scales)
library(ggimage)
library(showtext)
library(sysfonts)
library(base64enc)

font_add_google(
  family = "Roboto",
  regular.wt = 400,
  "Roboto"
)

showtext_auto()

setwd("~/Desktop/Data_Projects/nba_ml_salary_analysis")

worst_contracts_df <- read_csv(
  "~/Desktop/Data_Projects/nba_ml_salary_analysis/data/model_output/worst_value_contracts.csv",
  col_select = -1
)

library(gt)
library(gtExtras)

worst_contracts_table <- worst_contracts_df %>%
  mutate(
    Player_Image = paste0(
      logo,
      "|||",
      Images
    )
  ) %>%
  
  arrange(SurplusValuePct) %>%
  
  select(
    Player_Image,
    Player,
    team_abbr,
    Age,
    PTS,
    TRB,
    AST,
    Salary,
    PercentofCap,
    Expected_Salary,
    Expected_Percentage,
    SurplusValuePct
  ) %>%
  gt() %>%
  opt_table_font(
    font = list(
      google_font("Roboto")
    )
  ) %>%
  
  # Player image + team logo watermark
  text_transform(
    locations = cells_body(columns = Player_Image),
    fn = function(x) {
      sapply(x, function(val) {
        
        parts <- strsplit(val, "\\|\\|\\|")[[1]]
        
        logo <- parts[1]
        image <- parts[2]
        
        # Embed SVG logo
        logo_base64 <- base64enc::dataURI(
          file = logo,
          mime = "image/svg+xml"
        )
        
        # Embed player headshot
        image_base64 <- base64enc::dataURI(
          file = image,
          mime = "image/png"
        )
        
        htmltools::HTML(
          paste0(
            "<div style='position:relative; width:50px; height:50px;'>",
            
            # Team logo behind
            "<img src='", logo_base64,
            "' style='position:absolute; left:50%; transform:translateX(-50%); top:-15px; height:75px; opacity:0.50;'>",
            
            # Player headshot
            "<img src='", image_base64,
            "' style='position:absolute; left:50%; transform:translateX(-50%); top:-5px; height:60px;'>",
            
            "</div>"
          )
        )
      })
    }
  )  %>%
  
  # Salary in millions
  fmt_currency(
    columns = c(Salary, Expected_Salary),
    currency = "USD",
    decimals = 2,
    scale_by = 1e-6,
    suffixing = FALSE
  ) %>%
  
  # Cap percentages
  fmt_percent(
    columns = c(Expected_Percentage, PercentofCap),
    decimals = 1
  ) %>%
  
  # Surplus value formatting
  fmt(
    columns = SurplusValuePct,
    fns = function(x) {
      ifelse(
        x >= 0,
        sprintf("+%.1f%%", x),
        sprintf("%.1f%%", x)
      )
    }
  ) %>%
  
  data_color(
    columns = SurplusValuePct,
    colors = scales::col_numeric(
      palette = c("#F87171", "#FCFBF8", "#22C55E"),
      domain = c(min(-14), max(2))
    )
  ) %>%
  
  cols_label(
    Player_Image = "",
    Player = "Player",
    Salary = "Salary (M)",
    Expected_Salary = "Salary (M)",
    SurplusValuePct = "Value +/-",
    PercentofCap = "Cap %",
    Expected_Percentage = "Cap %",
    team_abbr = 'Team', 
    PTS = "PPG",
    TRB = "RPG",
    AST = "APG"
  ) %>%
  
  tab_spanner(
    label = "Current Contract",
    columns = c(Salary, PercentofCap)
  ) %>%
  
  tab_spanner(
    label = "Estimated Value",
    columns = c(Expected_Salary, Expected_Percentage)
  ) %>%
  
  cols_align(
    align = "center",
    columns = everything()
  ) %>%
  cols_align(
    align = "left",
    columns = c(Player_Image, Player)
  ) %>%
   
  tab_header(
    title = html(
      paste0(
        "<div style='position:relative;'>",
        "<span>The NBA's Worst Value Contracts</span>",
        "<img src='data:image/png;base64,",
        base64enc::base64encode(logo_path),
        "' style='position:absolute; right:-2px; top:-2px; height:50px;'>",
        "</div>"
      )
    ),
    subtitle = "Players whose 2025-26 salary exceeds their on-court impact"
  ) %>%
  
  tab_style(
    style = cell_text(
      size = px(12),
      weight = "bold"
    ),
    locations = cells_column_spanners()
  ) %>%
  
  tab_style(
    style = cell_text(
      weight = "bold",
      size = px(26)
    ),
    locations = cells_title(
      groups = "title"
    )
  ) %>%
  
  tab_style(
    style = cell_text(
      weight = "normal",
      size = px(16)
    ),
    locations = cells_title(
      groups = "subtitle"
    )
  ) %>%
  
  tab_style(
    style = cell_text(
      weight = "bold"
    ),
    locations = cells_column_labels()
  ) %>%
  
  tab_style(
    style = cell_borders(
      sides = "left",
      color = "#000000",
      style = "dotted",
      weight = px(1)
    ),
    locations = cells_body(
      columns = Salary
    )
  ) %>%
  
  tab_style(
    style = cell_borders(
      sides = "left",
      color = "#000000",
      style = "dotted",
      weight = px(1)
    ),
    locations = cells_column_labels(
      columns = Salary
    )
  ) %>%
  
  tab_style(
    style = cell_borders(
      sides = "right",
      color = "#000000",
      style = "dotted",
      weight = px(1)
    ),
    locations = cells_body(
      columns = PercentofCap
    )
  ) %>%
  
  tab_style(
    style = cell_borders(
      sides = "right",
      color = "#000000",
      style = "dotted",
      weight = px(1)
    ),
    locations = cells_column_labels(
      columns = PercentofCap
    )
  ) %>%
  
  opt_row_striping(
    row_striping = TRUE
  ) %>%
  
  tab_source_note(
    source_note = "Source: Spotrac & Basketball Reference"
  ) %>%
  
  tab_style(
    style = cell_text(
      size = px(14),
      style = "italic"
    ),
    locations = cells_source_notes()
  ) %>%
  
  cols_width(
    Player_Image ~ px(60),
    Player ~ px(140),
    team_abbr ~ px(45),
    Age ~ px(45),
    PTS ~ px(45),
    TRB ~ px(45),
    AST ~ px(45),
    Salary ~ px(75),
    PercentofCap ~ px(55),
    Expected_Salary ~ px(75),
    Expected_Percentage ~ px(55),
    SurplusValuePct ~ px(65)
  ) %>%
  
  tab_options(
    heading.align = "left",
    table.background.color = "#FCFBF8",
    heading.background.color = "#FCFBF8",
    row.striping.include_table_body = TRUE,
    row.striping.background_color = "#FFFFFF",
    heading.title.font.size = 22,
    heading.subtitle.font.size = 12,
    table.width = pct(100),
    data_row.padding = px(4)
  )

worst_contracts_table

gtsave(
  worst_contracts_table,
  "images/worst_contract_values.png"
)