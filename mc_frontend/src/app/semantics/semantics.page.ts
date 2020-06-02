import {AfterViewInit, Component} from '@angular/core';
import {NavController, ToastController} from '@ionic/angular';
import {HelperService} from '../helper.service';
import configMC from '../../configMC';
import {HttpClient, HttpErrorResponse, HttpParams} from '@angular/common/http';
import {ActivatedRoute} from '@angular/router';
import {CorpusService} from '../corpus.service';
import {VectorNetworkForm} from '../../../openapi';

@Component({
    selector: 'app-semantics',
    templateUrl: './semantics.page.html',
    styleUrls: ['./semantics.page.scss'],
})
export class SemanticsPage implements AfterViewInit {
    public highlightRegex = '';
    public highlightSet: Set<string> = new Set<string>();
    public isKWICview = false;
    public kwicGraphs: string;
    public metadata: string[] = ('XII panegyrici Latini\n' +
        'Baehrens, Emil\n' +
        'Lipsiae | 1874 | Teubner\n' +
        'Augsburg, Staats- und Stadtbibliothek -- LR 759\n' +
        'URL: https://reader.digitale-sammlungen.de/de/fs1/object/display/bsb11265534_00133.html\n' +
        'Permalink: http://mdz-nbn-resolving.de/urn:nbn:de:bvb:12-bsb11265534-1').split('\n');
    public minCount = 1;
    public nearestNeighborCount = 1;
    public searchRegex = '';
    public similarContexts: string[][] = [];
    public svgElementSelector = '#svg';

    constructor(public navCtrl: NavController,
                public helperService: HelperService,
                public http: HttpClient,
                public toastCtrl: ToastController,
                public activatedRoute: ActivatedRoute,
                public corpusService: CorpusService) {
    }

    getSimilarContexts(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            const vnf: VectorNetworkForm = {
                search_regex: this.searchRegex,
                nearest_neighbor_count: Math.max(Math.round(this.nearestNeighborCount), 1)
            };
            const formData: FormData = new FormData();
            Object.keys(vnf).forEach((key: string) => formData.append(key, vnf[key]));
            const semanticsUrl: string = configMC.backendBaseUrl + configMC.backendApiVectorNetworkPath;
            this.similarContexts = [];
            this.helperService.makePostRequest(this.http, this.toastCtrl, semanticsUrl, formData).then((contexts: string[][]) => {
                this.similarContexts = contexts;
                this.highlightSet = new Set<string>();
                if (this.highlightRegex) {
                    const regex: RegExp = new RegExp(this.highlightRegex);
                    this.similarContexts.forEach((context: string[]) => {
                        context.forEach((tok: string) => {
                            if (regex.test(tok)) {
                                this.highlightSet.add(tok);
                            }
                        });
                    });
                }
                return resolve();
            }, () => {
                return reject();
            });
        });
    }

    getWhiteSpace(): string {
        return ' ';
    }

    ngAfterViewInit(): Promise<void> {
        return new Promise<void>(resolve => {
            this.activatedRoute.queryParams.subscribe((params: any) => {
                if (Object.keys(params).length) {
                    Object.keys(params).forEach((key: string) => {
                        this[key] = typeof this[key] === 'number' ? +params[key] : params[key];
                    });
                    this.updateView();
                }
                return resolve();
            });
        });
    }

    updateVectorNetwork(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            let params: HttpParams = new HttpParams().set('search_regex', this.searchRegex);
            params = params.set('min_count', (Math.max(Math.round(this.minCount), 1)).toString());
            params = params.set('highlight_regex', this.highlightRegex);
            params = params.set('nearest_neighbor_count', (Math.max(Math.round(this.nearestNeighborCount), 1)).toString());
            const semanticsUrl: string = configMC.backendBaseUrl + configMC.backendApiVectorNetworkPath;
            const svgElement: SVGElement = document.querySelector(this.svgElementSelector);
            svgElement.innerHTML = '';
            this.helperService.makeGetRequest(this.http, this.toastCtrl, semanticsUrl, params).then((svgString: string) => {
                this.kwicGraphs = svgString;
                svgElement.innerHTML = this.kwicGraphs;
                return resolve();
            }, (error: HttpErrorResponse) => {
                if (error.status === 422) {
                    this.helperService.showToast(this.toastCtrl, this.corpusService.tooManyHitsString).then();
                }
                return reject();
            });
        });
    }

    updateView(): void {
        if (!this.searchRegex) {
            this.helperService.showToast(this.toastCtrl, this.corpusService.searchRegexMissingString).then();
        } else {
            if (this.isKWICview) {
                this.getSimilarContexts().then();
            } else {
                this.updateVectorNetwork().then();
            }
        }
    }
}
