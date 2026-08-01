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

# NBA Salary Cap History
salary_cap <- tibble(
  Season = c(
    "1984-85","1985-86","1986-87","1987-88","1988-89","1989-90",
    "1990-91","1991-92","1992-93","1993-94","1994-95","1995-96",
    "1996-97","1997-98","1998-99","1999-00","2000-01","2001-02",
    "2002-03","2003-04","2004-05","2005-06","2006-07","2007-08",
    "2008-09","2009-10","2010-11","2011-12","2012-13","2013-14",
    "2014-15","2015-16","2016-17","2017-18","2018-19","2019-20",
    "2020-21","2021-22","2022-23","2023-24","2024-25","2025-26",
    "2026-27"
  ),
  Salary_Cap = c(
    3600000,
    4233000,
    4945000,
    6164000,
    7232000,
    9802000,
    11871000,
    12500000,
    14000000,
    15175000,
    15964000,
    23000000,
    24363000,
    26900000,
    30000000,
    34000000,
    35500000,
    42500000,
    40271000,
    43840000,
    43870000,
    49500000,
    53135000,
    55630000,
    58680000,
    57700000,
    58044000,
    58044000,
    58679000,
    58679000,
    63065000,
    70000000,
    94143000,
    99093000,
    101869000,
    109140000,
    109140000,
    112414000,
    123655000,
    136021000,
    140588000,
    154647000,
    164961000
  )
)

tv_deal_x <- which(salary_cap$Season == "2015-16") + 0.5
second_apron_x <- which(salary_cap$Season == "2023-24") + 0.5

# Plot
plot <- ggplot(
  salary_cap,
  aes(
    x = Season,
    y = Salary_Cap
  )
) +
  geom_col(
    aes(fill = Salary_Cap),
    color = "white",
    linewidth = 0.3,
    width = 0.8
  ) +
  scale_fill_gradient(
    low = "#B7E4C7",
    high = "#0B6E4F"
  ) +
  geom_vline(
    xintercept = which(salary_cap$Season == "2015-16") + 0.5,
    linetype = "dashed",
    linewidth = .8,
    color = "#4A5568"
  ) +
  annotate(
    "text",
    x = tv_deal_x - 0.5,
    y = 105000000,
    label = "New TV Deal Begins",
    hjust = 1,
    size = 8,
    fontface = "bold",
    color = "#4A5568"
  ) +
  geom_vline(
    xintercept = which(salary_cap$Season == "2023-24") + 0.5,
    linetype = "dashed",
    linewidth = .8,
    color = "#4A5568"
  ) +
  annotate(
    "text",
    x = second_apron_x - 0.5,
    y = 150000000,
    label = "Second Apron Introduced",
    hjust = 1,
    size = 8,
    fontface = "bold",
    color = "#4A5568"
  ) +
  scale_y_continuous(
    labels = dollar_format(
      scale = 1e-6,
      suffix = "M"
    )
  ) +
  scale_x_discrete(
    breaks = salary_cap$Season[seq(1, nrow(salary_cap), by = 4)]
  ) +
  labs(
    title = "NBA Salary Cap Growth",
    subtitle = "The financial landscape of the NBA has transformed dramatically since 1984",
    x = NULL,
    y = "Salary Cap",
    caption = "Source: Spotrac"
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
    plot.title = element_text(
      size = 56,
      face = "bold"
    ),
    plot.subtitle = element_text(
      size = 30
    ),
    axis.text.x = element_text(
      angle = 45,
      hjust = 1,
      size = 20
    ),
    axis.text.y = element_text(
      size = 20
    ),
    axis.title.y = element_text(
      face = "bold",
      size = 30
    ),
    plot.caption = element_text(
      family = "Roboto",
      size = 28,
      hjust = 0,
      face = "bold"
    ),
    legend.position = "none"
  )

plot

ggsave(
  filename = "images/salary_cap_growth.png",
  plot = plot,
  width = 8,
  height = 5,
  dpi = 300,
  bg = "#FCFBF8"
)