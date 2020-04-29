/* tslint:disable:variable-name */
export class TextComplexity {
    public avg_w_len: number;
    public avg_w_per_sent: number;
    public lex_den: number;
    public n_abl_abs: number;
    public n_clause: number;
    public n_gerund: number;
    public n_inf: number;
    public n_part: number;
    public n_punct: number;
    public n_sent: number;
    public n_subclause: number;
    public n_types: number;
    public n_w: number;
    public pos: number;

    constructor(init?: Partial<TextComplexity>) {
        Object.assign(this, init);
    }
}
