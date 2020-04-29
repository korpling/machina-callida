/* tslint:disable:variable-name */
export class NodeMC {
    public annis_node_name: string;
    public annis_node_type: string;
    public annis_tok: string;
    public annis_type: string;
    public id: string;
    public udep_lemma: string;
    public udep_upostag: string;
    public udep_xpostag: string;
    public udep_feats: string;
    public solution: string;
    public is_oov: boolean;
    constructor(init?: Partial<NodeMC>) {
        Object.assign(this, init);
    }
}
