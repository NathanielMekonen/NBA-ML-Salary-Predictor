library(tidyverse)
library(ggpmisc)
library(showtext)
library(sysfonts)

font_add_google(
  family = "Roboto",
  regular.wt = 400,
  "Roboto"
)

showtext_auto()

setwd("~/Desktop/Data_Projects/nba_ml_salary_analysis")

player_stats <- read_csv(
  "data/model_output/player_stats_and_expected_salary.csv"
)

# Stats you want to compare against salary
stats_to_show <- c(
  "MP",
  "PER",
  "USG%",
  "OWS",
  "DWS",
  "WS/48",
  "OBPM",
  "BPM",
  "VORP",
  "season_number",
  "ScoringVolume",
  "PlaymakingVolume",
  "TurnoverVolume",
  "ImpactMinutes",
  "EfficientScoring",
  "OffensiveCreation"
)

# Convert to long format
plot_df <- player_stats %>%
  select(
    PercentofCap,
    all_of(stats_to_show)
  ) %>%
  pivot_longer(
    cols = -PercentofCap,
    names_to = "Stat",
    values_to = "Value"
  ) %>%
  drop_na()

# Calculate R² for each stat
r2_df <- plot_df %>%
  group_by(Stat) %>%
  summarise(
    R2 = cor(Value, PercentofCap)^2,
    .groups = "drop"
  ) %>%
  arrange(desc(R2))

# Join R² back in
plot_df <- plot_df %>%
  left_join(r2_df, by = "Stat")

# Order facets by R²
plot_df$Stat <- factor(
  plot_df$Stat,
  levels = r2_df$Stat
)

# Rename facet labels
plot_df$Stat <- recode(
  plot_df$Stat,
  "MP" = "Minutes per Game",
  "USG%" = "Usage Rate",
  "OWS" = "Offensive Win Shares",
  "DWS" = "Defensive Win Shares",
  "WS/48" = "Win Shares per 48",
  "OBPM" = "Offensive BPM",
  "season_number" = "Season Number",
  "ScoringVolume" = "Scoring Volume",
  "PlaymakingVolume" = "Playmaking Volume",
  "TurnoverVolume" = "Turnover Volume",
  "ImpactMinutes" = "Impact Minutes",
  "EfficientScoring" = "Scoring Efficiency",
  "OffensiveCreation" = "Offensive Creation"
)

# Plot
stats_plot <- ggplot(
  plot_df,
  aes(x = Value, y = PercentofCap)
) +
  geom_point(
    aes(color = R2),
    alpha = 0.35,
    size = 1.5
    
  ) +
  scale_color_gradientn(
    colors = c("#F40B0B", "#B063F8", "#074A9C"),
    name = "R²"
  ) +
  geom_smooth(
    aes(color = R2),
    method = "lm",
    se = FALSE,
    linewidth = 0.4
  ) +
  stat_poly_eq(
    aes(
      label = paste(..rr.label..)
    ),
    formula = y ~ x,
    parse = TRUE,
    size = 14,
    label.x = 0.05,
    label.y = 0.95,
    fontface = "bold"
  ) +
  facet_wrap(
    ~ Stat,
    scales = "free_x",
    ncol = 4
  ) +
  theme_minimal(base_family = "Roboto") +
  theme(
    panel.grid.minor = element_blank(),
    strip.text = element_text(
      face = "bold",
      size = 36
    ),
    axis.text = element_text(size = 30),
    axis.title = element_text(
      size = 48,
      face = "bold"
    ),
    plot.title = element_text(
      face = "bold",
      size = 84
    ),
    plot.subtitle = element_text(size = 54),
    legend.position = "none",
    plot.background = element_rect(
      fill = "#FCFBF8",
      color = NA
    ),
    panel.background = element_rect(
      fill = "#FCFBF8",
      color = NA
    )
  ) +
  labs(
    title = "NBA Statistics vs Salary Cap %",
    subtitle = "2025-26 stats ranked by individual explanatory power (R²)",
    x = "2025-26 Regular Season Stats",
    y = "% of Salary Cap"
  )

stats_plot

ggsave( 
  "images/salary_stat_correlations.png", 
  stats_plot, 
  width = 12, 
  height = 10, 
  dpi = 300 
)
