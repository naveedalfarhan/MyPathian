angular.module("pathianApp.services")
    .factory("equipmentService", ["$resource",
        function($resource) {
            return $resource("/api/equipment/:id", // Define the base url, adding a parameter for the id
                { 
                    id: "@id", 
                    equipment_id: "@equipment_id", 
                    paragraph_id: "@paragraph_id",
                    raf_id: "@raf_id",
                    reset_schedule_id: "@reset_schedule_id"
                }, // Set up the parameters in the url -- in this case, map the id to the model's id, indicated by the @ sign
                {
                    'update': { method: "PUT" },
                    'getParagraph': {
                        method: "GET",
                        url: "/api/equipment/paragraphs/:id"
                    },
                    'getAllForGroup': {
                        method: "GET",
                        url: "/api/groups/:group_id/equipment",
                        isArray: "true"
                    },
                    'getAllParagraphsForType': {
                        method: "GET",
                        url: "/api/equipment/:equipment_id/paragraphs/:type"
                    },
                    'moveParagraphUp': {
                        method: "POST",
                        url: "/api/equipment/:equipment_id/paragraphs/:paragraph_id/moveup"
                    },
                    'moveParagraphDown': {
                        method: "POST",
                        url: "/api/equipment/:equipment_id/paragraphs/:paragraph_id/movedown"
                    },
                    'addParagraph': {
                        method: "PUT",
                        url: "/api/equipment/:equipment_id/paragraphs/:paragraph_id"
                    },
                    'insertParagraph': {
                        method: "PUT",
                        url: "/api/equipment/paragraphs"
                    },
                    'updateParagraph': {
                        method: "PUT",
                        url: "/api/equipment/paragraphs/:id"
                    },
                    'deleteParagraph': {
                        method: "POST",
                        url: "/api/equipment/:equipment_id/paragraphs/:paragraph_id/delete"
                    },
                    "getMappedPoints": {
                        method: "GET",
                        isArray: true,
                        url: "/api/equipment/:equipment_id/mapped_points"
                    },
                    "getUnmappedPoints": {
                        method: "GET",
                        isArray: true,
                        url: "/api/equipment/:equipment_id/unmapped_points"
                    },
                    "getEquipmentPoints": {
                        method: "GET",
                        url: "/api/equipment/:equipment_id/allPoints"
                    },
                    'getRafPressures': {
                        method: "GET",
                        url: "/api/equipment/:equipment_id/raf"
                    },
                    'insertRafPressure': {
                        method: "PUT",
                        url: "/api/equipment/raf"
                    },
                    'deleteRafPressure': {
                        method: "DELETE",
                        url: "/api/equipment/raf/:raf_id"
                    },
                    'getResetSchedules': {
                        method: "GET",
                        url: "/api/equipment/:equipment_id/rs"
                    },
                    'insertResetSchedule': {
                        method: "PUT",
                        url: "/api/equipment/:equipment_id/rs/:reset_schedule_id"
                    },
                    'deleteResetSchedule': {
                        method: "DELETE",
                        url: "/api/equipment/:equipment_id/rs/:reset_schedule_id"
                    },
                    'getEquipmentIssues': {
                        method: "GET",
                        url: "/api/equipment/:equipment_id/ci"
                    },
                    'insertEquipmentIssue': {
                        method: "PUT",
                        url: "/api/equipment/:equipment_id/ci"
                    },
                    'updateEquipmentIssue': {
                        method: "PUT",
                        url: "/api/equipment/ci/:equipment_issue_id"
                    },
                    'deleteEquipmentIssue': {
                        method: "DELETE",
                        url: "/api/equipment/ci/:equipment_issue_id"
                    },
                    'getEquipmentTasks': {
                        method: "GET",
                        url: "/api/equipment/:equipment_id/ct"
                    },
                    'insertEquipmentTask': {
                        method: "PUT",
                        url: "/api/equipment/:equipment_id/ct"
                    },
                    'updateEquipmentTask': {
                        method: "PUT",
                        url: "/api/equipment/ct/:equipment_task_id"
                    },
                    'deleteEquipmentTask': {
                        method: "DELETE",
                        url: "/api/equipment/ct/:equipment_task_id"
                    }
                }
            );
        }
    ]);
