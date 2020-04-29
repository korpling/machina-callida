/* tslint:disable:variable-name */
export class LinkMC {
    public annis_component_name: string;
    public annis_component_type: string;
    public source: string;
    public target: string;
    public udep_deprel: string;
    constructor(init?: Partial<LinkMC>) {
        Object.assign(this, init);
    }
}
