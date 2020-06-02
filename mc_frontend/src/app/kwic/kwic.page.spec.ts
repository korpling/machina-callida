import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {KwicPage} from './kwic.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {APP_BASE_HREF} from '@angular/common';

describe('KwicPage', () => {
    let kwicPage: KwicPage;
    let fixture: ComponentFixture<KwicPage>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [KwicPage],
            imports: [
                HttpClientModule,
                IonicStorageModule.forRoot(),
                RouterModule.forRoot([]),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
        })
            .compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(KwicPage);
        kwicPage = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(kwicPage).toBeTruthy();
        const svgElement: SVGElement = document.querySelector(kwicPage.svgElementSelector);
        expect(svgElement.innerHTML).toBeFalsy();
        kwicPage.exerciseService.kwicGraphs = '<svg></svg>';
        kwicPage.initVisualization();
        expect(svgElement.innerHTML).toBeTruthy();
    });
});
