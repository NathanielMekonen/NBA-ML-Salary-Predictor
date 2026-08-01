library(tidyverse)
library(scales)
library(ggimage)
library(showtext)
library(sysfonts)

font_add_google(
  family = "Roboto",
  regular.wt = 400,
  "Roboto"
)

showtext_auto()

setwd("~/Desktop/Data_Projects/nba_ml_salary_analysis")

salary_df <- read_csv(
  "~/Desktop/Data_Projects/nba_ml_salary_analysis/data/final/all_league_salaries.csv",
  col_select = -1
)

salary_df <- salary_df %>%
  mutate(
    year = as.numeric(substr(season, 1, 4)),
    league = str_to_upper(league)
  )

head(salary_df)

league_labels <- salary_df %>%
  group_by(league) %>%
  filter(year == max(year))

# Create dataframe for final season league labels/logos
league_labels <- salary_df %>%
  group_by(league) %>%
  filter(year == max(year)) %>%
  ungroup() %>%
  mutate(
    logo = case_when(
      league == "NBA" ~ normalizePath("images/nba_logo.png"),
      league == "NFL" ~ normalizePath("images/nfl_logo.png"),
      league == "MLB" ~ normalizePath("images/mlb_logo.png"),
      league == "NHL" ~ normalizePath("images/nhl_logo.png")
    ),
    logo_x = year + 2,
    logo_y = case_when(
      league == "NBA" ~ 11000000,
      league == "NFL" ~ 4000000,
      league == "MLB" ~ 2800000,
      league == "NHL" ~ 5500000
    )
  )


# Create chart
salary_chart <- ggplot(
  salary_df,
  aes(
    x = year,
    y = avg_salary,
    color = league
  )
) +
  
  geom_line(
    linewidth = 1.3
  ) +
  
  # Connector lines
  geom_segment(
    data = league_labels,
    inherit.aes = FALSE,
    aes(
      x = year,
      xend = logo_x - 0.2,
      y = avg_salary,
      yend = logo_y
    ),
    color = "gray50",
    linewidth = 0.5,
    linetype = "dotted"
  ) +
  
  # Non-NBA logos
  geom_image(
    data = league_labels %>% filter(league != "NBA"),
    inherit.aes = FALSE,
    aes(
      x = logo_x,
      y = logo_y,
      image = logo
    ),
    size = 0.1
  ) +
  
  # Smaller NBA logo
  geom_image(
    data = league_labels %>% filter(league == "NBA"),
    inherit.aes = FALSE,
    aes(
      x = logo_x,
      y = logo_y,
      image = logo
    ),
    size = 0.075
  ) +
  
  scale_color_manual(
    values = c(
      "NBA" = "#1E3A8A",
      "MLB" = "#E01E26",
      "NFL" = "#117A2B",
      "NHL" = "#111111"
    )
  ) +
  
  scale_x_continuous(
    expand = c(0, 0),
    limits = c(2012, max(salary_df$year) + 3),
    breaks = seq(2012, max(salary_df$year), by = 2)
  ) +
  
  scale_y_continuous(
    labels = label_dollar(
      scale = 1e-6,
      suffix = "M"
    )
  ) +
  
  labs(
    title = "The NBA's Salary Explosion",
    subtitle = "Average player salaries across the four major leagues since 2012",
    x = NULL,
    y = "Average Player Salary",
    color = NULL,
    caption = "Source: Spotrac"
  ) +
  
  theme_minimal(
    base_size = 14,
    base_family = "Roboto"
  ) +
  
  theme(
    text = element_text(
      family = "Roboto"
    ),
    
    plot.title = element_text(
      family = "Roboto",
      size = 56,
      hjust = 0,
      face = "bold"
    ),
    
    plot.subtitle = element_text(
      family = "Roboto",
      size = 30,
      hjust = 0
    ),
    
    axis.text = element_text(
      family = "Roboto",
      size = 36
    ),
    
    axis.title = element_text(
      family = "Roboto",
      size = 30,
      face = "bold"
    ),
    
    axis.line = element_line(
      color = "#666666",
      linewidth = 0.5
    ),
    
    plot.caption = element_text(
      family = "Roboto",
      size = 28,
      hjust = 0,
      face = "bold"
    ),
    
    legend.position = "none",
    
    panel.grid.minor = element_blank(),
    
    panel.background = element_rect(
      fill = "#FCFBF8",
      color = NA
    ),
    
    plot.background = element_rect(
      fill = "#FCFBF8",
      color = NA
    ),
    
    plot.margin = margin(
      10,
      80,
      10,
      10
    )
  )

salary_chart

ggsave(
  filename = "images/average_salaries_chart.png",
  plot = salary_chart,
  width = 8,
  height = 5,
  dpi = 300,
  bg = "#FCFBF8"
)