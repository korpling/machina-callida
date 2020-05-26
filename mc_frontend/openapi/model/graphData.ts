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
import { NodeMC } from './nodeMC';
import { Link } from './link';


/**
 * Nodes, edges and metadata for a graph.
 */
export interface GraphData { 
    /**
     * Whether edges in the returned graph are directed.
     */
    directed?: boolean;
    /**
     * Additional graph data.
     */
    graph?: object;
    /**
     * List of edges for the graph.
     */
    links: Array<Link>;
    /**
     * Whether the graph consists of multiple subgraphs.
     */
    multigraph?: boolean;
    /**
     * List of nodes for the graph.
     */
    nodes: Array<NodeMC>;
}
