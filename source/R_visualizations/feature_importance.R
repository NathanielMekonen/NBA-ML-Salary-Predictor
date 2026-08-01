library(tidyverse)
library(scales)
library(showtext)
library(sysfonts)

font_add_google(
  family = "Roboto",
  regular.wt = 400,
  "Roboto"
)

showtext_auto()

setwd("~/Desktop/Data_Projects/nba_ml_salary_analysis")

feature_importance <- read_csv(
  "data/model_output/feature_importance.csv"
)

top_features <- feature_importance %>%
  arrange(desc(Importance)) %>%
  slice_head(n = 10) %>%
  mutate(
    Feature_Label = recode(
      Feature,
      "MP" = "Minutes per Game",
      "OBPM" = "Offensive BPM",
      "OffensiveCreation" = "Offensive Creation",
      "season_number" = "Season Number",
      "RookieScale" = "Rookie Contract",
      "PER" = "PER",
      "USG%" = "Usage Rate",
      "ImpactMinutes" = "Impact Minutes",
      "EfficientScoring" = "Scoring Efficiency",
      "FT%" = "Free Throw %"
    ),
    Feature_Label = factor(
      Feature_Label,
      levels = Feature_Label %>% rev()
    ), 
    Importance_Label = percent(
      Importance,
      accuracy = 0.1
    )
  )

# Create chart
features_chart <- ggplot(
  top_features,
  aes(
    x = Importance,
    y = Feature_Label
  )
) +
  
  geom_col(
    aes(fill = Importance),
    width = 0.65
  ) +
  
  scale_fill_gradient(
    low = "#F7E08C",
    high = "#B8860B"
  ) +
  
  geom_text(
    aes(
      label = Importance_Label
    ),
    hjust = -0.15,
    family = "Roboto",
    size = 12,
    color = "#333333"
  ) +
  
  scale_x_continuous(
    labels = percent_format(accuracy = 1),
    expand = expansion(mult = c(0, .15))
  ) +
  
  labs(
    title = "NBA Salary Model Feature Importance",
    subtitle = "Top 10 factors driving predicted player value",
    x = NULL,
    y = NULL,
    caption = "Source: NBA Salary Prediction Model"
  ) +
  
  theme_minimal(base_family = "Roboto") +
  
  theme(
    plot.background = element_rect(
      fill = "#FCFBF8",
      color = NA
    ),
    
    panel.background = element_rect(
      fill = "#FCFBF8",
      color = NA
    ),
    
    panel.grid.major.x = element_line(
      color = "#D9D9D9",
      linewidth = 0.4
    ),
    
    panel.grid.major.y = element_line(
      color = "#EAEAEA",
      linewidth = 0.3
    ),
    
    panel.grid = element_blank(),
    
    legend.position = "none",
    
    axis.text.y = element_text(
      size = 30,
      color = "#2D2D2D"
    ),
    
    axis.text.x = element_blank(),
    
    plot.title = element_text(
      size = 56,
      face = "bold",
      hjust = 0
    ),
    
    plot.subtitle = element_text(
      size = 30,
      hjust = 0
    ),
    
    plot.caption = element_text(
      family = "Roboto",
      size = 28,
      hjust = 0,
      face = "bold"
    ),
    
    plot.margin = margin(
      20, 30, 20, 20
    )
  )

features_chart

ggsave(
  filename = "images/feature_importance.png",
  plot = features_chart,
  width = 8,
  height = 5,
  dpi = 300,
  bg = "#FCFBF8"
)