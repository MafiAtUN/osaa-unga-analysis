"""
Question sets and prompts for UNGA analysis
"""

from typing import List, Dict


def get_suggestion_questions(country: str, classification: str) -> List[str]:
    """Get compelling suggestion questions based on country and classification."""
    
    # Base questions for all countries
    base_questions = [
        # Multi-year analysis questions (prioritized)
        "Compare this speech with their speeches from the past 5 years",
        "What trends can be observed in this country's UNGA statements over time?",
        "How has their focus on climate change evolved in recent years?",
        "What changes in their diplomatic priorities can be seen compared to previous sessions?",
        "How has their approach to international cooperation changed from previous years?",
        "What new themes or priorities emerged compared to past speeches?",
        "How has this country's position evolved since their previous UNGA speech?",
        "What are the priorities and key topics discussed compared to last year's speech?",
        "Analyze the evolution of this country's stance on global governance over the past decade",
        "How has their emphasis on sustainable development changed since 2015?",
        "What patterns can be identified in their UNGA speeches from 2010-2024?",
        "Compare their current priorities with speeches from the 1990s and 2000s",
        "How has their approach to multilateralism evolved since the Cold War era?",
        "What continuity and change can be observed in their diplomatic language over 20 years?",
        "How has their focus on peace and security issues shifted since the 1990s?",
        "What generational changes in leadership priorities are reflected in their speeches?",
        "How has their engagement with global challenges evolved since the Millennium Development Goals?",
        "What historical context from their past speeches helps explain current positions?",
        "How has their relationship with international organizations changed over time?",
        "What long-term trends in their foreign policy can be identified from UNGA speeches?",
        # Current analysis questions
        "What specific SDGs were mentioned in this speech?",
        "What were the main challenges discussed for achieving sustainable development?",
        "What partnerships or collaborations were proposed?",
        "How did they address climate change and environmental issues?",
        "What role did they see for multilateralism and international cooperation?",
        "How did they discuss youth empowerment and inclusion?",
        "What were their views on digital transformation and AI?",
        "How did they address gender equality and women's empowerment?"
    ]
    
    # African Member State specific questions
    if classification == "African Member State":
        african_questions = [
            "How did they discuss Agenda 2063 and African integration?",
            "What specific African development priorities were highlighted?",
            "How did they address peace and security in Africa?",
            "What role did they see for the African Union?",
            "How did they discuss debt relief and financial support for Africa?",
            "What were their views on African youth and education?",
            "How did they address food security and agricultural development?",
            "What partnerships did they propose with other African countries?"
        ]
        return base_questions + african_questions
    
    # Development Partner specific questions
    else:
        partner_questions = [
            "How did they address their commitment to Africa's development?",
            "What specific support did they offer to African countries?",
            "How did they discuss their partnership with African institutions?",
            "What role did they see for international cooperation in Africa?",
            "How did they address global inequality and development gaps?",
            "What were their views on South-South cooperation?",
            "How did they discuss technology transfer to developing countries?",
            "What commitments did they make to support the SDGs in Africa?"
        ]
        return base_questions + partner_questions


def get_cross_year_topics_and_questions() -> Dict[str, List[str]]:
    """Get all topics and their associated questions for cross-year analysis."""
    return {
        "🧭 Issue Salience Over Time": [
            "How has the focus on climate change evolved from 1946 to 2025?",
            "Which topics saw the biggest rise in mentions in the last decade?",
            "What issues dominated the speeches during the Cold War period?",
            "How did interest in AI and technology change after 2015?",
            "What were the top five most-discussed topics during the 1970s oil crisis?",
            "How did peace and security discourse shift after major wars or conflicts?",
            "Which themes declined the most over the past 20 years?",
            "Compare the salience of development vs security topics over time.",
            "How did African countries' priorities change after the launch of Agenda 2063?",
            "Which issues consistently appear across all decades?"
        ],
        
        "🌍 Country Positioning and Ideological Shifts": [
            "How has the rhetorical position of the United States changed since 1946?",
            "Which countries are closest in speech similarity to China in 2025?",
            "Did African countries move closer or further from Western countries in tone after 1990?",
            "How did Russia's speech themes shift after the breakup of the USSR?",
            "Which nations show the largest ideological movement between 1970 and 2025?",
            "Which regions share the most similar rhetoric on climate action?",
            "Has the G77 bloc become more unified or diverse in its positions over time?",
            "How does India's UNGA stance compare with Pakistan's across decades?",
            "How did European Union members align or diverge on global governance themes?",
            "Identify countries whose rhetoric has become more development-focused over time."
        ],
        
        "🤝 Similar Speech Analysis": [
            "Which countries have speeches most similar to Kenya's in 2023?",
            "Who shared the closest speech pattern with France during the 2015 UNGA?",
            "What developing nations use rhetoric closest to Brazil on environmental issues?",
            "Which countries sound most like the African Union representative in tone and themes?",
            "Find clusters of countries that share similar language on human rights.",
            "Which small island states align most with EU rhetoric on climate finance?",
            "Identify countries whose speeches echo the U.S. across multiple decades.",
            "What set of countries most resemble South Africa's stance post-apartheid?",
            "How did the similarity network shift before and after the COVID-19 pandemic?",
            "Which regions are linguistically or semantically closest in their diplomatic tone?"
        ],
        
        "🕸️ Regional and Coalition Comparisons": [
            "How do African and Asian countries differ in priorities at the UNGA?",
            "Compare G77 and OECD rhetoric on financing for development.",
            "What are the main shared issues across SADC, ECOWAS, and EAC members?",
            "How do European and Latin American countries differ on migration?",
            "Which regions focus most on sovereignty and non-interference?",
            "Compare the Arab League and EU speeches on Palestine.",
            "Do Caribbean nations emphasize climate change more than trade?",
            "How aligned are BRICS members in their UNGA speeches?",
            "What unites and separates African nations' rhetoric on debt relief?",
            "Which regional blocs show the highest internal variation in topics?"
        ],
        
        "🧩 Topic Composition (Per Speech or Country)": [
            "What percentage of Ghana's 2020 speech was about sustainable development?",
            "Break down Japan's 2023 speech by topic proportions.",
            "How did Nigeria's focus on security vs development evolve over time?",
            "Which countries devote the largest share of their speeches to climate issues?",
            "What share of African speeches mention Agenda 2063?",
            "Which countries dedicate most time to human rights in 2025?",
            "How balanced are the topics in Canada's recent UNGA speeches?",
            "What is the dominant theme in Bangladesh's 2022 statement?",
            "Compare topic shares for Kenya in 1975 vs 2025.",
            "Identify countries whose speeches are dominated by one or two themes."
        ],
        
        "🗣️ Keyword and Phrase Trajectories": [
            "When did 'Sustainable Development Goals' start appearing in speeches?",
            "How often is the term 'climate finance' used, and by whom?",
            "Track mentions of 'Palestine' vs 'Israel' since 1946.",
            "What's the trend of using 'multilateralism' across decades?",
            "Which countries most frequently mention 'AI' or 'artificial intelligence'?",
            "When did 'Agenda 2063' first appear in UNGA discourse?",
            "Which regions use the term 'sovereignty' the most?",
            "How has the phrase 'South-South cooperation' evolved over time?",
            "What new policy buzzwords emerged after 2020?",
            "Which issues are seeing rapid growth in mentions recently?"
        ],
        
        "💬 Sentiment, Tone, and Emotion": [
            "How optimistic or pessimistic were the speeches in 2024 compared to 2023?",
            "Which regions express the most concern or urgency about global crises?",
            "What's the emotional tone difference between developed and developing countries?",
            "Which years had the most 'negative' tone globally?",
            "How does African nations' tone shift after major economic shocks?",
            "Which topics elicit the strongest emotional language?",
            "Has diplomatic tone become more confrontational or cooperative since 2000?",
            "Compare tone during Cold War years vs post-Cold War period.",
            "Do small island states use more emotional appeals than others?",
            "Identify speeches that are unusually hopeful or critical for their time."
        ],
        
        "🔗 Country–Topic Network Analysis": [
            "Which countries talk most about AI or digital transformation?",
            "Build a network linking countries to topics they focus on the most.",
            "Who are the top contributors to climate finance discourse?",
            "Which countries rarely discuss human rights?",
            "Identify cross-issue linkages: e.g., security + food or trade + climate.",
            "Which African countries link gender equality with economic policy?",
            "What global clusters exist between countries and their top issues?",
            "How do regional alliances shape shared issue networks?",
            "Find countries connected by frequent co-mentions of migration and development.",
            "Which countries talk about the widest range of topics each year?"
        ],
        
        "🧠 Co-mention and Entity Networks": [
            "Which countries are most frequently mentioned together?",
            "What entities are most associated with UN reform discussions?",
            "Track co-mentions of United States and China over time.",
            "How often do African countries reference the European Union?",
            "Which nations often appear in context with conflict or sanctions?",
            "Who are the most frequently co-mentioned global leaders?",
            "What patterns exist between donor countries and recipient regions?",
            "How often are UN agencies like UNDP or UNHCR referenced?",
            "Which conflicts are most referenced alongside humanitarian terms?",
            "Identify emerging partnerships from frequent co-mentions."
        ],
        
        "⏱️ Event-Aligned Timeline Analysis": [
            "How did speeches change during the COVID-19 pandemic?",
            "What was the reaction to the Iraq War (2003) across regions?",
            "How did the tone shift after the fall of the Berlin Wall?",
            "Did 2008 speeches reflect the global financial crisis?",
            "How did 2022 UNGA speeches react to the Ukraine war?",
            "Which crises generated the biggest spikes in mentions of 'peace'?",
            "How did climate rhetoric respond to the Paris Agreement (2015)?",
            "What global events correspond with major shifts in sentiment?",
            "How did pandemic-era speeches differ from pre-pandemic ones?",
            "What new priorities emerged after 9/11?"
        ],
        
        "🧍 Speaker Metadata and Protocol Patterns": [
            "Which countries are most often represented by heads of state vs ministers?",
            "How has the share of female speakers changed over time?",
            "Do longer speeches tend to come from certain regions or ranks?",
            "How many first-time speakers appeared in the last five years?",
            "Which years had the highest total number of speeches?",
            "Are certain days of the debate dominated by particular regions?",
            "What countries deliver the most emotional or formal speeches?",
            "Do speech lengths correlate with tone or topics?",
            "What is the average speaking time by region or income group?",
            "Which years saw the largest participation drop?"
        ],
        
        "📊 Cross-Year and Cross-Topic Comparison": [
            "Compare climate and trade discourse in 1990 vs 2020.",
            "How do speeches from small states differ from major powers?",
            "Which issues show the greatest divergence between North and South?",
            "Compare the emphasis on SDGs before and after 2015.",
            "Which decade saw the most balanced topic distribution?",
            "What themes unify the Least Developed Countries (LDCs) group?",
            "How did focus shift from colonialism to globalization over time?",
            "Compare speeches before and after Agenda 2063 for African states.",
            "What new themes dominate the 2020s compared to 1980s?",
            "Which regions became more aligned on multilateral cooperation?"
        ],
        
        "👩‍🎤 Gender and Equality": [
            "How has the frequency of gender-related terms ('gender equality,' 'women's empowerment,' 'girls' education,' etc.) changed from 1946 to 2025?",
            "Which countries most frequently mention gender equality or women's rights in their UNGA speeches?",
            "How do developed and developing countries differ in the way they talk about gender issues?",
            "Which regions show the most consistent emphasis on women's participation in peace and security?",
            "Did the tone or intensity of gender references shift after landmark events like Beijing 1995, CEDAW adoption, or UNSCR 1325 (Women, Peace & Security)?",
            "Which leaders or heads of state have made gender equality a major theme in their speeches?",
            "Do speeches by female heads of state or ministers differ in tone or topic distribution from those by male counterparts?",
            "How often are gender issues linked with other themes such as education, development, climate change, or conflict?",
            "Which countries or groups (e.g., G77, EU, AU) have pushed for stronger gender mainstreaming language in recent decades?",
            "Has the framing of gender discourse evolved—from 'women's protection' and 'welfare' to 'empowerment,' 'leadership,' and 'rights'?"
        ]
    }


def get_country_and_group_questions() -> Dict[str, Dict[str, List[str]]]:
    """Get questions organized by country/group selection with two-level structure."""
    return {
        "Individual Countries": {
            "🌍 Global Governance & Multilateralism": [
                "How has this country's position on multilateralism evolved over time?",
                "What role does this country see for international organizations in peace and security?",
                "How has this country's approach to global economic governance changed?",
                "What are the key themes in this country's UNGA speeches regarding global governance?",
                "How does this country view UN reform and institutional changes?"
            ],
            "🌱 Development & Climate": [
                "How has this country's approach to development assistance changed over time?",
                "How has this country's stance on climate change evolved in UNGA speeches?",
                "What are this country's priorities regarding sustainable development goals?",
                "How does this country address the relationship between development and environmental protection?",
                "What role does this country see for climate finance and technology transfer?"
            ],
            "🤝 Regional Cooperation & Integration": [
                "What role does this country see for regional cooperation and integration?",
                "How has this country's approach to regional organizations evolved?",
                "What are the key partnerships and alliances this country emphasizes in its speeches?",
                "How does this country balance regional and global commitments?",
                "What role does this country play in regional peace and security initiatives?"
            ],
            "⚖️ Human Rights & Social Issues": [
                "How has this country's rhetoric on human rights evolved over time?",
                "What are this country's positions on gender equality and women's empowerment?",
                "How does this country address migration and refugee issues?",
                "What role does this country see for social protection and inclusion?",
                "How has this country's stance on education and health evolved?"
            ],
            "🔍 Current Priorities & Concerns": [
                "What are the main priorities and concerns expressed by this country in recent years?",
                "How has this country's foreign policy focus shifted over time?",
                "What emerging issues does this country emphasize in its speeches?",
                "How does this country address global challenges and crises?",
                "What vision does this country present for international cooperation?"
            ],
            "👩‍🎤 Gender and Equality": [
                "How has the frequency of gender-related terms ('gender equality,' 'women's empowerment,' 'girls' education,' etc.) changed from 1946 to 2025?",
                "Which countries most frequently mention gender equality or women's rights in their UNGA speeches?",
                "How do developed and developing countries differ in the way they talk about gender issues?",
                "Which regions show the most consistent emphasis on women's participation in peace and security?",
                "Did the tone or intensity of gender references shift after landmark events like Beijing 1995, CEDAW adoption, or UNSCR 1325 (Women, Peace & Security)?",
                "Which leaders or heads of state have made gender equality a major theme in their speeches?",
                "Do speeches by female heads of state or ministers differ in tone or topic distribution from those by male counterparts?",
                "How often are gender issues linked with other themes such as education, development, climate change, or conflict?",
                "Which countries or groups (e.g., G77, EU, AU) have pushed for stronger gender mainstreaming language in recent decades?",
                "Has the framing of gender discourse evolved—from 'women's protection' and 'welfare' to 'empowerment,' 'leadership,' and 'rights'?"
            ]
        },
        "Country Groups": {
            "African Union Members": {
                "🌍 African Integration & Agenda 2063": [
                    "How has the African Union's collective position on Agenda 2063 evolved?",
                    "What are the main themes in AU members' speeches regarding African integration?",
                    "How has the AU approach to continental free trade changed over time?",
                    "What role do AU members see for pan-African institutions?",
                    "How has the AU stance on African unity evolved in UNGA speeches?"
                ],
                "🕊️ Peace & Security in Africa": [
                    "How has the AU approach to peace and security changed over time?",
                    "What role do AU members see for African solutions to African problems?",
                    "How has the AU stance on conflict prevention evolved?",
                    "What are AU members' positions on peacekeeping and peacebuilding?",
                    "How does the AU address terrorism and violent extremism?"
                ],
                "🌱 Development & Climate": [
                    "How has the AU stance on climate change evolved in UNGA speeches?",
                    "What role do AU members see for South-South cooperation?",
                    "How has the AU approach to sustainable development changed?",
                    "What are AU members' positions on financing for development?",
                    "How does the AU address food security and agriculture?"
                ]
            },
            "G77 Members": {
                "💰 Development Financing & Economic Justice": [
                    "How has the G77's position on development financing evolved since 1964?",
                    "What are the main themes in G77 speeches regarding global economic governance?",
                    "How has the G77 approach to debt relief changed over time?",
                    "What role do G77 members see for international financial institutions?",
                    "How has the G77 stance on trade and development evolved?"
                ],
                "🌍 South-South Cooperation": [
                    "What role do G77 members see for South-South cooperation?",
                    "How has the G77 approach to multilateralism changed over time?",
                    "What are G77 members' positions on technology transfer?",
                    "How does the G77 address capacity building and technical assistance?",
                    "What role does the G77 see for emerging economies in global affairs?"
                ],
                "🌱 Climate Justice & Environment": [
                    "How has the G77 stance on climate justice evolved in UNGA speeches?",
                    "What are G77 members' positions on climate finance and adaptation?",
                    "How does the G77 address environmental protection and development?",
                    "What role do G77 members see for common but differentiated responsibilities?",
                    "How has the G77 approach to sustainable development changed?"
                ]
            },
            "European Union Members": {
                "🌍 Multilateralism & Global Governance": [
                    "How has the EU's position on multilateralism evolved since the 1990s?",
                    "What are the main themes in EU speeches regarding global governance?",
                    "How has the EU approach to international cooperation changed over time?",
                    "What role do EU members see for regional integration globally?",
                    "How has the EU stance on international law evolved?"
                ],
                "🌱 Development & Climate Action": [
                    "How has the EU approach to development cooperation changed over time?",
                    "How has the EU stance on climate action evolved in UNGA speeches?",
                    "What role do EU members see for green transition and sustainability?",
                    "How does the EU address global health and pandemic preparedness?",
                    "What are EU members' positions on digital transformation and development?"
                ],
                "⚖️ Human Rights & Values": [
                    "How has the EU stance on human rights evolved in UNGA speeches?",
                    "What role do EU members see for democracy and rule of law?",
                    "How does the EU address gender equality and women's empowerment?",
                    "What are EU members' positions on migration and refugee protection?",
                    "How has the EU approach to conflict prevention and peacebuilding changed?"
                ]
            },
            "BRICS Members": {
                "🌍 Global Economic Governance": [
                    "How has BRICS' position on global economic governance evolved since 2009?",
                    "What are the main themes in BRICS speeches regarding multipolarity?",
                    "How has the BRICS approach to international financial institutions changed?",
                    "What role do BRICS members see for emerging economies in global affairs?",
                    "How has the BRICS stance on global trade evolved?"
                ],
                "🤝 Development Cooperation": [
                    "How has the BRICS approach to development cooperation changed over time?",
                    "What role do BRICS members see for South-South cooperation?",
                    "How does BRICS address technology transfer and capacity building?",
                    "What are BRICS members' positions on infrastructure development?",
                    "How has the BRICS stance on sustainable development evolved?"
                ],
                "🔧 UN Reform & Global Institutions": [
                    "How has the BRICS stance on UN reform evolved in UNGA speeches?",
                    "What role do BRICS members see for global governance reform?",
                    "How does BRICS address international security and peacekeeping?",
                    "What are BRICS members' positions on global health governance?",
                    "How has the BRICS approach to climate change evolved?"
                ]
            },
            "Small Island Developing States": {
                "🌊 Climate Change & Ocean Governance": [
                    "How has SIDS' position on climate change evolved since the 1990s?",
                    "How has the SIDS approach to ocean governance changed over time?",
                    "What role do SIDS see for international cooperation in climate adaptation?",
                    "How does SIDS address sea-level rise and coastal protection?",
                    "What are SIDS' positions on climate finance and loss and damage?"
                ],
                "🌱 Sustainable Development": [
                    "What are the main themes in SIDS speeches regarding sustainable development?",
                    "How has the SIDS stance on financing for development evolved in UNGA speeches?",
                    "What role do SIDS see for renewable energy and green technology?",
                    "How does SIDS address biodiversity and ecosystem protection?",
                    "What are SIDS' positions on tourism and sustainable economic development?"
                ],
                "🤝 International Cooperation": [
                    "What role do SIDS see for multilateral cooperation in addressing their challenges?",
                    "How has the SIDS approach to partnerships with developed countries evolved?",
                    "What are SIDS' positions on technology transfer and capacity building?",
                    "How does SIDS address global health and pandemic preparedness?",
                    "What role do SIDS see for regional cooperation and integration?"
                ]
            }
        }
    }


