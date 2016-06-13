# Figure 1 for 'Complexity Science and Legal Systems' Submitted to Science (June 2016)
# J.B. Ruhl, Daniel Martin Katz, Michael J. Bommarito II 

# Note: This should be executed from the root of the repository.

# Required packages
# install.packages("ggplot2")
# install.packages("plyr")
# install.packages("reshape")
# install.packages("gridExtra")
# install.packages("ggthemes")
# install.packages("extrafont")
# install.packages("gridBase")

# Tested version:
# > version
# _                                          
# platform       x86_64-w64-mingw32                         
# arch           x86_64                                     
# os             mingw32                                    
# system         x86_64, mingw32                            
# status         Revised                                    
# major          3                                          
# minor          2.4                                        
# year           2016                                       
# month          03                                         
# day            16                                         
# svn rev        70336                                      
# language       R                                          
# version.string R version 3.2.4 Revised (2016-03-16 r70336)
# nickname       Very Secure Dishes    

# Load libraries
library(ggplot2)
library(plyr)
library(reshape2)
library(gridExtra)
library(ggthemes)
library(extrafont)
library(gridBase)

# Load section and token counts
section_ts <- read.csv("paper/section_ts.csv", header = F)
names(section_ts) <- c("year", "count")

token_ts <- read.csv("paper/token_ts.csv", header = F)
names(token_ts) <- c("year", "count")
token_ts$count <- token_ts$count / 1000000.0

#Here is a first cut with geom_point of the Growth in the Number of Sections in the United States Code
ggplot(section_ts, aes(year, count)) + geom_point(size=2, colour='red') + 
  labs(title="Growth in the Number of Sections in the United States Code") + 
  theme_gdocs()

#Now lets try a line drawing option
ggplot(section_ts, aes(year, count)) + geom_line(size=.5, colour='red') +
  labs(title="Growth in the Number of Sections in the United States Code") +
  theme_linedraw()

#We need to change the origin of the y axis - ylim(40000, 55000) 
ggplot(section_ts, aes(year, count)) + geom_line(size=.5, colour='red') + 
  labs(title="Growth in the Number of Sections in the United States Code") + 
  theme_light()  + 
  ylim(40000, 55000)

# Now we need the labels on the x axis to start in 1994 and end in 2014 
# So lets add this - + scale_x_continuous(breaks = round(seq(min(Fig1$Year), max(Fig1$Year), by = 5)))
ggplot(section_ts, aes(year, count)) + geom_line(size=.5, colour='red') +
  labs(title="Growth in the Number of Sections in the United States Code") +
  theme_light() +
  ylim(40000, 55000) +
  scale_x_continuous(breaks = round(seq(min(section_ts$year), max(section_ts$year), by = 5)))

#Lets try a new theme - from ggthemes package and review the result 
section_figure <- ggplot(section_ts, aes(year, count)) + geom_line(size=.5, colour='red') +
  labs(title="Growth in the Number of Sections in the United States Code") +
  theme_fivethirtyeight() +
  ylim(40000, 55000) +
  scale_x_continuous(breaks = round(seq(min(section_ts$year), max(section_ts$year), by = 5)))
section_figure

# Now lets clean up title, background color, etc. 
# Will do this step by step so the user can see the corrispondence between the code and changes in the Figure 
section_figure <- section_figure + theme(plot.title = element_text(size=8,lineheight=4, vjust=1,family="sans"))
section_figure
section_figure <- section_figure + theme(panel.background=element_rect(fill='white'))
section_figure
section_figure <- section_figure + theme(plot.background=element_rect(fill="white"))
section_figure

#Lets put a bit more padding around our graph 
section_figure <-section_figure + theme(plot.margin=unit(c(1,1,1,1),"cm"))
section_figure
#We will come back to this in just a second and put it together with the graph below  


#Okay here is the starting plot for the Words in the Overall United States Code 
ggplot(token_ts, aes(year, count)) + 
  geom_line(size=.5, colour='red') + 
  labs(title="Growth in the Number of Words in the United States Code") + 
  theme_linedraw()

#We need to change the origin of the y axis - ylim(15, 30) 
ggplot(token_ts, aes(year, count)) + 
  geom_line(size=.5, colour='red') + 
  labs(title="Growth in the Number of Words in the United States Code") + 
  theme_light() + 
  ylim(15, 30)

# Now we need the labels on the x axis to start in 1994 and end in 2014 
# So lets add this - + scale_x_continuous(breaks = round(seq(min(Fig1$Year), max(Fig1$Year), by = 5)))
ggplot(token_ts, aes(year, count)) + 
  geom_line(size=.5, colour='red') + 
  labs(title="Growth in the Number of Words in the United States Code") + 
  theme_light() + 
  ylim(15, 30) + 
  scale_x_continuous(breaks = round(seq(min(token_ts$year), max(token_ts$year), by = 5)))

#Lets try a new theme - from ggthemes package and review the result 
token_figure <- ggplot(token_ts, aes(year, count)) + 
  geom_line(size=.5, colour='red') + 
  labs(title="Growth in the Number of Words in the United States Code") + 
  theme_fivethirtyeight() + 
  scale_y_continuous(breaks=c(15, 20, 25, 30), labels=c("15m", "20m", "25m", "30m")) + 
  scale_x_continuous(breaks = round(seq(min(token_ts$year), max(token_ts$year), by = 5)))

# Now lets clean up title, background color, etc. 
# Will do this step by step so the user can see the corrispondence between the code and changes in the Figure Words2 <- Words + theme(plot.title = element_text(size=8,lineheight=4, vjust=1,family="sans"))
token_figure <- token_figure + theme(plot.title = element_text(size=8,lineheight=4, vjust=1,family="sans"))
token_figure <- token_figure + theme(panel.background=element_rect(fill='white'))
token_figure <- token_figure + theme(plot.background=element_rect(fill="white"))
token_figure
#Lets put a bit more padding around our graph 
token_figure <- token_figure + theme(plot.margin=unit(c(1,1,1,1),"cm"))
token_figure

#Okay so now we have the pieces in place 
#Lets grid this up into a double plot for comparison purposes 
final_figure <- grid.arrange(section_figure, token_figure, ncol=1)
ggsave(file="figure_1.pdf", final_figure)
