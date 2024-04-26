!constant ORGANISATION_NAME "Vidio dot com"
!constant GROUP_NAME "Vidio Chatbot System"

workspace "Vidio Chatbot" "This is chatbot from Vidio." {
    model {
        group "${ORGANISATION_NAME} - ${GROUP_NAME}" {
            user = person "Person" "A user of chatbot."
            chatbotSystem = softwareSystem "Chatbot System" "Chatbot system." "Chatbot System" {
                vidioChat = container "Vidio Chat" "Vidio Chat" "Kotlin"
                chatbotApi = container "API" "Chatbot API" "Flask Python" ""
                chatbotDb = container "Database Chatbot" "Chatbot DB" "Postgres AlloyDB" "Database"
                chatbotWorker = container "Worker" "Chatbot Worker" "Celery Python"
            }
            vidioRecommendationSystem = softwareSystem "Vidio RecSys" "Vidio Recommendation System" "Recommendation System" {
                larvaApi = container "API" "Larva API" "Flask Python"
                larvaDb = container "Database Larva" "Larva DB" "Postgres" "Database"
                larvaApi -> larvaDb "Reads user play history"
            }

            user -> vidioChat "Uses"
            chatbotApi -> chatbotWorker "Enqueue"
            chatbotWorker -> chatbotDb "Reads from" "SQL"
            chatbotWorker -> chatbotDb "Writes to" "SQL"
            chatbotWorker -> larvaApi "Get user play history" "HTTP"
            chatbotWorker -> vidioChat "Sends reply" "HTTP"

            live = deploymentEnvironment "Live" {
                deploymentNode "Google Cloud" {
                    tags "Google Cloud"
                    deploymentNode "asia-southeast1" {
                        tags "Google Cloud - Region"

                        deploymentNode "GCP Kubernetes Engine" {
                            tags "Google Cloud Platform - Kubernetes Engine"
                            
                            vidioChatInstance = containerInstance vidioChat
                            chatbotApiInstance = containerInstance chatbotApi
                            chatbotWorkerInstance = containerInstance chatbotWorker
                            recommendationApiInstance = containerInstance larvaApi
                        }

                        deploymentNode "GCP AlloyDB" {
                            tags "Google Cloud Platform - Cloud SQL"

                            chatbotDbInstance = containerInstance chatbotDb
                        }
                        lb = infrastructureNode "GCP Cloud Load Balancing" {
                            tags "Google Cloud Platform - Cloud Load Balancing"
                        }
                        gemini = infrastructureNode "GCP Vertex AI - Gemini Pro" {
                            tags "Google Cloud Platform - AI Platform"
                        }
                        searchConversation = infrastructureNode "GCP Agent Builder - Search" {
                            tags "Google Cloud Platform - Cloud SDK"
                        }
                    }
                }
                lb -> vidioChatInstance "Forwards request to" "HTTP"
                lb -> chatbotApiInstance "Forwards request to" "HTTP"
                chatbotWorkerInstance -> searchConversation "Search for Content, Schedule, FAQ" "HTTPS"
                chatbotWorkerInstance -> gemini "Semantic routing, Recommendation, Summarize FAQ, Content, Schedule" "HTTPS/Protobuf"
            }
        }

    }

    views {
        deployment * live {
            include *
        }

        theme https://static.structurizr.com/themes/google-cloud-platform-v1.5/theme.json

        styles {
            element "Database" {
                shape Cylinder
                background #08427b
                color #ffffff
            }
        }
    }
}