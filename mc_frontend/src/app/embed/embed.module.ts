import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { EmbedPageRoutingModule } from './embed-routing.module';

import { EmbedPage } from './embed.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    EmbedPageRoutingModule
  ],
  declarations: [EmbedPage]
})
export class EmbedPageModule {}
