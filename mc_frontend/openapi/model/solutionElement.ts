/**
 * Machina Callida Backend REST API
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


/**
 * Target or value of a correct solution for an exercise.
 */
export interface SolutionElement { 
    /**
     * Content of the solution element.
     */
    content?: string;
    /**
     * Unique identifier for the node in the SALT model.
     */
    salt_id?: string;
    /**
     * Unique identifier for the sentence in a corpus.
     */
    sentence_id: number;
    /**
     * Unique identifier for the token in a sentence.
     */
    token_id: number;
}

